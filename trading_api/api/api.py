import os
from datetime import timezone, datetime, timedelta
from decimal import Decimal

from django.db.backends.utils import logger
from django.db.models import Q, Sum
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet

from .models import User, Text, Symbol, Account, Broker, Order, Rates, Withdraw, Requisite, Deal, UserRate, Dispute
from .serializers import UserSerializer, TextSerializer, SymbolSerializer, UserAccountsSerializer, \
    AggregatedOrderSerializer, OrderSerializer, BrokerSerializer, OrderDetailSerializer, UserInfoSerializer, \
    RequisiteSerializer, DealDetailSerializer, RatesSerializer
from crypto.manager import crypto_manager

from utils.redis_queue import NotificationsQueue


class TgUserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'telegram_id'


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'nickname'


class NewUserView(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data['telegram_id']
        ref_code = request.data.get('ref')
        user = User.objects.filter(telegram_id=telegram_id).first()
        if user is None:
            referred_from = User.objects.filter(ref_code=ref_code).first() if ref_code else None
            user = User.objects.create(telegram_id=telegram_id)
            if referred_from:
                user.referred_from = referred_from
            user.save()
        return Response(UserSerializer(user).data, status=HTTP_201_CREATED)


class SymbolsViewSet(ReadOnlyModelViewSet):
    serializer_class = SymbolSerializer
    queryset = Symbol.objects.filter(is_active=True).all()


class BrokersViewSet(ReadOnlyModelViewSet):
    serializer_class = BrokerSerializer
    queryset = Broker.objects.all()


class UserAccountsViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserAccountsSerializer
    queryset = User.objects.all()


class AggregatedOrderView(APIView):
    def get(self, request, *args, **kwargs):
        order_type = self.request.query_params.get('type')
        symbol = get_object_or_404(Symbol, id=self.request.query_params.get('symbol'))
        ref = get_object_or_404(User, id=self.request.query_params.get('ref'))
        data = AggregatedOrderSerializer(Broker.objects, context={'type': order_type, 'symbol': symbol, 'ref': ref}, many=True).data
        return Response(data=data)


class OrderViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        order_type = self.request.query_params.get('type')
        symbol = get_object_or_404(Symbol.objects.filter(is_active=True), id=self.request.query_params.get('symbol'))
        broker = get_object_or_404(Broker, id=self.request.query_params.get('broker'))
        ref = get_object_or_404(User, id=self.request.query_params.get('ref'))
        return Order.objects.filter(
            broker=broker,
            symbol=symbol,
            type=order_type,
            is_deleted=False,
            is_active=True,
            is_system_active=True
        ).order_by(f'{"-" if order_type == "buy" else ""}rate')


class UserOrdersViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        base = user.orders.filter(is_deleted=False)
        if 'symbol' in self.request.query_params:
            symbol = get_object_or_404(Symbol.objects.filter(is_active=True), id=self.request.query_params['symbol'])
            base = base.filter(symbol=symbol)
        return base.order_by('created_at')

    def perform_destroy(self, instance: Order):
        instance.is_deleted = True
        instance.save()

    def perform_update(self, serializer: OrderSerializer):
        if coeff := serializer.validated_data.get('coefficient'):
            serializer.validated_data['rate'] = Rates.objects.filter(symbol=serializer.instance.symbol).get().rate * Decimal(coeff)
        serializer.save()


class UserBrokerView(APIView):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        broker = get_object_or_404(Broker, id=kwargs['broker_id'])
        target = Requisite.objects.filter(user=user, broker=broker).first()
        if target:
            return Response(data=RequisiteSerializer(target).data)
        else:
            raise NotFound

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        broker = get_object_or_404(Broker, id=kwargs['broker_id'])
        requisite = request.data['requisite']
        add_info = request.data.get('add_info')
        target, created = Requisite.objects.update_or_create(user=user, broker=broker, defaults={'requisite': requisite, 'add_info': add_info})
        return Response(data=RequisiteSerializer(target).data)


class OrderInfoViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.filter(is_deleted=False)


class UserInfoViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserInfoSerializer
    queryset = User.objects.all()
    lookup_field = 'nickname'


class NewOrderView(APIView):
    def post(self, request, *args, **kwargs):
        brokers = Broker.objects.filter(id__in=request.data['brokers']).all()
        symbol = get_object_or_404(Symbol.objects.filter(is_active=True), id=request.data['symbol'])
        limit_from = request.data['limit_from']
        limit_to = request.data['limit_to']
        order_type = request.data['type']
        if coefficient := request.data.get('coefficient'):
            rate = Rates.objects.filter(symbol=symbol).get().rate * Decimal(coefficient)
        else:
            rate = request.data['rate']
        user = get_object_or_404(User, id=request.data['user_id'])
        orders = []
        for broker in brokers:
            new_order = Order(
                broker=broker, symbol=symbol, limit_from=limit_from,
                limit_to=limit_to, type=order_type, user=user,
                rate=rate, coefficient=coefficient, is_system_active=order_type == 'buy'
            )
            orders.append(new_order)
        Order.objects.bulk_create(orders)
        return Response(status=HTTP_204_NO_CONTENT)


class GenerateAccountView(APIView):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.data.get('user_id'))
        symbol = get_object_or_404(Symbol.objects.filter(is_active=True), id=request.data.get('symbol'))
        if Account.objects.filter(user=user, symbol=symbol).exists():
            raise ValidationError
        if symbol.name == 'usdt':
            symbol_eth = Symbol.objects.get(name='eth')
            ethereum_account, _ = Account.objects.get_or_create(
                user=user, symbol=symbol_eth, defaults={'private_key': crypto_manager['eth'].generate_wallet()}
            )
            pk = ethereum_account.private_key
        else:
            args = []
            if symbol.name == 'prizm':
                args.append(user.id)
            pk = crypto_manager[symbol.name].generate_wallet(*args)
        Account.objects.create(user=user, symbol=symbol, private_key=pk)
        return Response(status=HTTP_204_NO_CONTENT)


class ValidateAddressMixin:
    def validate_address(self, address: str, symbol: Symbol):
        if not self.is_address_valid(address, symbol):
            raise ValidationError

    def is_address_valid(self, address: str, symbol: Symbol):
        return crypto_manager.is_address_valid(symbol.name, address)


class BalanceManagementMixin:
    def get_account(self, user: User, symbol: Symbol):
        return user.accounts.filter(symbol=symbol).get()

    def get_system_user(self):
        return User.objects.filter(telegram_id=int(os.environ.get('SYSTEM_USER_TG'))).get()

    def add_commission(self, amount: Decimal, symbol: Symbol, notify=True):
        user = self.get_system_user()
        self.add_balance(amount, user, symbol)
        if notify:
            NotificationsQueue.put(
                {
                    'telegram_id': user.telegram_id,
                    'type': 'new_commission_system',
                    'amount': amount,
                    'symbol': symbol.name.upper()
                }
            )

    def is_account_exists(self, user: User, symbol: Symbol):
        return user.accounts.filter(symbol=symbol).exists()

    def validate_balance(self, user: User, symbol: Symbol, target_amount: Decimal):
        account = self.get_account(user, symbol)
        if account.balance < target_amount:
            raise ValidationError

    def validate_account_change(self, account):
        if account.frozen < 0 or account.balance < 0:
            raise ValidationError(f'User {account.user.nickname} has balance or frozen < 0')

    def freeze(self, amount, user, symbol):
        account = self.get_account(user, symbol)
        account.balance -= amount
        account.frozen += amount
        self.validate_account_change(account)
        account.save()

    def unfreeze(self, amount, user, symbol):
        account = self.get_account(user, symbol)
        account.balance += amount
        account.frozen -= amount
        self.validate_account_change(account)
        account.save()

    def add_frozen(self, amount, user, symbol):
        logger.info(f'adding frozen {amount} {symbol.name} to /_{user.nickname}')
        account = self.get_account(user, symbol)
        account.frozen += amount
        self.validate_account_change(account)
        account.save()

    def add_balance(self, amount, user, symbol):
        logger.info(f'adding balance {amount} {symbol.name} to /_{user.nickname}')
        account = self.get_account(user, symbol)
        account.balance += amount
        self.validate_account_change(account)
        account.save()


class AddressCheckView(APIView, ValidateAddressMixin):
    def post(self, request, *args, **kwargs):
        symbol = get_object_or_404(Symbol, id=request.data['symbol'])
        address = request.data['address']
        is_valid = self.is_address_valid(address, symbol)
        return Response(data={'is_valid': is_valid})


class NewWithdrawView(APIView, ValidateAddressMixin, BalanceManagementMixin):
    def post(self, request, *args, **kwargs):
        symbol = get_object_or_404(Symbol.objects.filter(is_active=True), id=request.data['symbol'])
        user = get_object_or_404(User, id=request.data['user_id'])
        address = request.data['address']
        amount = Decimal(request.data['amount'])
        self.validate_address(address, symbol)
        target_amount = amount + symbol.commission
        self.validate_balance(user, symbol, target_amount)
        with atomic():
            self.freeze(target_amount, user, symbol)
            Withdraw.objects.create(user=user, amount=amount, address=address,
                                    symbol=symbol, commission_service=symbol.commission)
        return Response(status=HTTP_204_NO_CONTENT)


class DealDetailViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = DealDetailSerializer
    queryset = Deal.objects.all()


class NewDealView(APIView, BalanceManagementMixin):
    def _validate_new_deal(self, seller, symbol, amount_crypto):
        self.validate_balance(seller, symbol, amount_crypto)

    def post(self, request, *args, **kwargs):
        amount_crypto = Decimal(request.data['amount_crypto'])
        amount = Decimal(request.data['amount'])
        order = get_object_or_404(Order.objects.filter(is_active=True, is_deleted=False), id=request.data['order_id'])
        symbol = order.symbol
        amount_crypto_block = amount_crypto + round(amount_crypto * symbol.deals_commission, 8)
        amount_crypto_send = amount_crypto - round(amount_crypto * symbol.deals_commission, 8)
        rate = Decimal(request.data['rate'])
        requisite = request.data.get('requisite')
        add_info = request.data.get('add_info')
        buyer = get_object_or_404(User, id=request.data['buyer_id'])
        seller = get_object_or_404(User, id=request.data['seller_id'])
        if requisite is None:
            requisite = seller.requisites.filter(broker=order.broker).first()
            if requisite is None:
                raise ValidationError
            requisite = requisite.requisite
            add_info = add_info
        self._validate_new_deal(seller, symbol, amount_crypto_block)
        with atomic():
            self.freeze(amount_crypto_block, seller, symbol)
            deal = Deal.objects.create(
                seller=seller, buyer=buyer, order=order, rate=rate, requisite=requisite,
                amount_crypto=amount_crypto, amount_currency=amount, symbol=symbol,
                amount_crypto_blocked=amount_crypto_block, amount_crypto_send=amount_crypto_send, add_info=add_info
            )
            data = DealDetailSerializer(deal).data
            NotificationsQueue.put(
                {
                    'telegram_id': (buyer if order.type == 'buy' else seller).telegram_id,
                    'type': 'new_deal',
                    'data': data
                }
            )
        return Response(data=data)


class UpdateDealMixin(BalanceManagementMixin):
    target_statuses = []
    buyer_message_type = ''
    seller_message_type = ''
    saved_deal = None
    validate_ref = True

    @property
    def deal(self):
        if self.saved_deal is None:
            self.saved_deal = self.get_deal()
        return self.saved_deal

    def get_deal(self) -> Deal:
        q = Deal.objects.filter(status__in=self.target_statuses)
        if self.validate_ref:
            ref = get_object_or_404(User, id=self.request.data['ref'])
            q.filter(Q(buyer=ref) | Q(seller=ref))
        return get_object_or_404(q, id=self.kwargs['deal_id'])

    def process_ref_earning(self, ref, amount):
        self.add_balance(amount, ref, self.deal.symbol)
        NotificationsQueue.put(
            {
                'telegram_id': ref.telegram_id,
                'type': 'ref_earning',
                'referral': self.deal.buyer.nickname,
                'amount': amount,
                'symbol': self.deal.symbol.name.upper()
            }
        )
        acc = self.get_account(ref, self.deal.symbol)
        acc.earned_from_ref += amount
        acc.save()

    # noinspection DuplicatedCode
    def process_deal(self, deal):
        with atomic():
            deal.status = 3
            deal.save()
            self.add_frozen(-deal.amount_crypto_blocked, deal.seller, deal.symbol)
            commission = deal.amount_crypto_blocked - deal.amount_crypto_send

            if (ref := deal.buyer.referred_from) and self.is_account_exists(ref, deal.symbol):
                ref_part = deal.buyer.referred_from.ref_part
                to_ref = round((deal.amount_crypto - deal.amount_crypto_send) * ref_part, 8)
                self.process_ref_earning(ref, to_ref)
                commission = commission - to_ref

            if (ref := deal.seller.referred_from) and self.is_account_exists(ref, deal.symbol):
                ref_part = deal.seller.referred_from.ref_part
                to_ref = round((deal.amount_crypto_blocked - deal.amount_crypto) * ref_part, 8)
                self.process_ref_earning(ref, to_ref)
                commission = commission - to_ref

            deal.commission = commission
            deal.closed_at = datetime.now(timezone.utc)
            self.add_balance(deal.amount_crypto_send, deal.buyer, deal.symbol)
            self.add_commission(commission, deal.symbol)
            self.send_notifications()

    def return_deal(self, deal):
        with atomic():
            deal.status = -1
            deal.save()
            self.unfreeze(deal.amount_crypto_blocked, deal.seller, deal.symbol)
            self.send_notifications()

    def _send_notification(self, telegram_id, message_type, add_data=None):
        if add_data is None:
            add_data = {}
        for mt in message_type:
            NotificationsQueue.put(
                {
                    'telegram_id': telegram_id,
                    'type': mt,
                    'data': DealDetailSerializer(self.deal).data,
                    **add_data
                }
            )

    def send_notifications(self):
        if self.buyer_message_type:
            if not isinstance(self.buyer_message_type, tuple):
                self.buyer_message_type = (self.buyer_message_type,)
            self._send_notification(self.deal.buyer.telegram_id, self.buyer_message_type)

        if self.seller_message_type:
            if not isinstance(self.seller_message_type, tuple):
                self.seller_message_type = (self.seller_message_type,)
            self._send_notification(self.deal.seller.telegram_id, self.seller_message_type)


class ConfirmDealView(APIView, UpdateDealMixin):
    target_statuses = [0]
    buyer_message_type = ('deal_accepted', 'requisite_only')

    def post(self, request, *args, **kwargs):
        with atomic():
            self.deal.status = 1
            self.deal.save()
            self.send_notifications()
        return Response(status=204)


class DeclineDealView(APIView, UpdateDealMixin):
    target_statuses = [0]
    buyer_message_type = 'deal_declined'
    seller_message_type = 'deal_declined'

    def post(self, request, *args, **kwargs):
        self.return_deal(self.deal)
        return Response(status=204)


class SendFiatDealView(APIView, UpdateDealMixin):
    target_statuses = [1]
    seller_message_type = 'fiat_sent'

    def post(self, request, *args, **kwargs):
        with atomic():
            self.deal.status = 2
            self.deal.save()
            self.send_notifications()
        return Response(status=204)


class OpenDisputeView(APIView, UpdateDealMixin):
    target_statuses = [2]

    def post(self, request, *args, **kwargs):
        ref = get_object_or_404(User, id=self.request.data['ref'])
        is_exists = Dispute.objects.filter(deal=self.deal).exists()
        if is_exists:
            raise ValidationError
        else:
            Dispute.objects.create(deal=self.deal, initiator=ref)
            self.send_notifications()
        return Response(status=204)

    def send_notifications(self):
        telegram_ids = [
            {'telegram_id': self.deal.seller.telegram_id, 'admin': False},
            {'telegram_id': self.deal.buyer.telegram_id, 'admin': False}
        ]
        for admin in User.objects.filter(is_admin=True).all():
            telegram_ids.append({'telegram_id': admin.telegram_id, 'admin': True})
        for telegram_id in telegram_ids:
            self._send_notification(
                telegram_id['telegram_id'],
                message_type=('dispute_opened',),
                add_data={'admin': telegram_id['admin']}
            )


class SendCryptoDealView(APIView, UpdateDealMixin):
    target_statuses = [2]
    seller_message_type = 'crypto_sent'
    buyer_message_type = 'crypto_received'

    def post(self, request, *args, **kwargs):
        self.process_deal(self.deal)
        return Response(status=204)


class SolveDisputeView(APIView, UpdateDealMixin):
    target_statuses = [2]
    validate_ref = False

    def post(self, request, *args, **kwargs):
        action = request.data['action']
        if action == 'seller':
            self.seller_message_type = 'dispute_closed_for_seller'
            self.buyer_message_type = 'dispute_closed_for_seller'
            self.return_deal(self.deal)

        elif action == 'buyer':
            self.seller_message_type = 'dispute_closed_for_buyer'
            self.buyer_message_type = 'dispute_closed_for_buyer'
            self.process_deal(self.deal)

        return Response(status=204)


class NewMessageView(APIView):
    def post(self, request, *args, **kwargs):
        sender = get_object_or_404(User, id=request.data['sender_id'])
        receiver = get_object_or_404(User, id=request.data['receiver_id'])
        text = request.data['text']
        file_id = request.data.get('file_id')
        photo_id = request.data.get('photo_id')
        NotificationsQueue.put(
            {
                'telegram_id': receiver.telegram_id,
                'type': 'message_received',
                'text': text,
                'file_id': file_id,
                'photo_id': photo_id,
                'user': {'nickname': sender.nickname, 'id': str(sender.id)}
            }
        )
        return Response(status=204)


class BalanceView(APIView):
    def get(self, request, *args, **kwargs):
        symbols = Symbol.objects.filter(is_active=True).all()
        data = []
        for symbol in symbols:
            try:
                target = {
                        'wallet': crypto_manager[symbol.name].get_balance(),
                        'db': symbol.accounts.aggregate(Sum('balance')).get('balance__sum') + symbol.accounts.aggregate(Sum('frozen')).get('frozen__sum'),
                        'symbol': symbol.name
                    }
                if symbol.name == 'usdt':
                    target['wallet'] += symbol.accounts.aggregate((Sum('wallet_balance'))).get('wallet_balance__sum')
            except Exception:
                continue
            target['balance'] = target['wallet'] - target['db']
            data.append(target)
        return Response(data=data)


class UsersStatView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'users': User.objects.count(),
            'users24h': User.objects.filter(created_at__gt=datetime.now(timezone.utc)-timedelta(days=1)).count()
        }
        return Response(data=data)


class RateUserView(APIView):
    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, id=kwargs['deal_id'])
        user = get_object_or_404(User, id=request.data['ref'])
        target = get_object_or_404(User, id=request.data['target'])
        is_like = request.data['is_like']
        if user in (deal.seller, deal.buyer) and target in (deal.seller, deal.buyer):
            UserRate.objects.get_or_create(deal=deal, user=user, target=target, defaults={'is_like': is_like})
        return Response(status=204)


class NicknameChangeView(APIView):
    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        new_nickname = request.data['nickname']
        is_exists = User.objects.filter(nickname=new_nickname).exists()
        if is_exists or 3 > len(new_nickname) > 10 or (
                user.last_nickname_change is not None and
                user.last_nickname_change + timedelta(days=30) > datetime.now(timezone.utc)
        ):
            raise ValidationError
        user.nickname = new_nickname
        user.last_nickname_change = datetime.now(timezone.utc)
        user.save()
        return Response(status=204)


class RatesViewSet(ReadOnlyModelViewSet):
    serializer_class = RatesSerializer
    queryset = Rates.objects.all()
    lookup_field = 'symbol'


class TextViewSet(ReadOnlyModelViewSet):
    serializer_class = TextSerializer
    queryset = Text.objects.all()
    lookup_field = 'name'
