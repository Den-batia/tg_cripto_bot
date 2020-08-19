from decimal import Decimal

from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet

from .models import User, Text, Symbol, Account, Broker, Order, Rates, Withdraw, Requisite
from .serializers import UserSerializer, TextSerializer, SymbolSerializer, UserAccountsSerializer, \
    AggregatedOrderSerializer, OrderSerializer, BrokerSerializer, OrderDetailSerializer, UserInfoSerializer, \
    RequisiteSerializer
from crypto.manager import crypto_manager


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
    queryset = Symbol.objects.all()


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
        data = AggregatedOrderSerializer(Broker.objects, context={'type': order_type, 'symbol': symbol}, many=True).data
        return Response(data=data)


class OrderViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        order_type = self.request.query_params.get('type')
        symbol = get_object_or_404(Symbol, id=self.request.query_params.get('symbol'))
        broker = get_object_or_404(Broker, id=self.request.query_params.get('broker'))
        return Order.objects.filter(broker=broker, symbol=symbol, type=order_type, is_deleted=False, is_active=True)


class UserOrdersViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        return user.orders.filter(is_deleted=False).order_by('created_at')

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
        broker = get_object_or_404(Broker, id=kwargs['broker'])
        target = Requisite.objects.filter(user=user, broker=broker).first()
        if target:
            return Response(data=RequisiteSerializer(target).data)
        else:
            raise NotFound

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        broker = get_object_or_404(Broker, id=kwargs['broker'])
        requisite = request.data['requisite']
        target, created = Requisite.objects.update_or_create(user=user, broker=broker, defaults={'requisite': requisite})
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
        symbol = get_object_or_404(Symbol, id=request.data['symbol'])
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
                rate=rate, coefficient=coefficient
            )
            orders.append(new_order)
        Order.objects.bulk_create(orders)
        return Response(status=HTTP_204_NO_CONTENT)


class GenerateAccountView(APIView):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.data.get('user_id'))
        symbol = get_object_or_404(Symbol, id=request.data.get('symbol'))
        if Account.objects.filter(user=user, symbol=symbol).exists():
            raise ValidationError
        Account.objects.create(user=user, symbol=symbol, private_key=crypto_manager[symbol.name].generate_wallet())
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


class AddressCheckView(APIView, ValidateAddressMixin):
    def post(self, request, *args, **kwargs):
        symbol = get_object_or_404(Symbol, id=request.data['symbol'])
        address = request.data['address']
        is_valid = self.is_address_valid(address, symbol)
        return Response(data={'is_valid': is_valid})


class NewWithdrawView(APIView, ValidateAddressMixin, BalanceManagementMixin):
    def post(self, request, *args, **kwargs):
        symbol = get_object_or_404(Symbol, id=request.data['symbol'])
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


class NewDealView(APIView, BalanceManagementMixin):
    def post(self, request, *args, **kwargs):
        amount_crypto = request.data['amount_crypto']
        amount_currency = request.data['amount_currency']
        order = get_object_or_404(Order.objects.filter(is_active=True, is_deleted=False), id=request.data['order_id'])
        symbol = get_object_or_404(Symbol, id=request.data['symbol_id'])
        rate = request.data['rate']
        initiator = get_object_or_404(User, )



class TextViewSet(ReadOnlyModelViewSet):
    serializer_class = TextSerializer
    queryset = Text.objects.all()
    lookup_field = 'name'
