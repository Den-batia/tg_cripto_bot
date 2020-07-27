from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from .models import User, Text, Symbol, Account, Broker, Order, Rates
from .serializers import UserSerializer, TextSerializer, SymbolSerializer, UserAccountsSerializer, \
    AggregatedOrderSerializer, OrderSerializer, BrokerSerializer
from crypto.manager import crypto_manager


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'telegram_id'


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
        print(order_type, symbol, broker, Order.objects.filter(broker=broker, symbol=symbol, type=order_type).count())
        return Order.objects.filter(broker=broker, symbol=symbol, type=order_type)


class NewOrderView(APIView):
    def post(self, request, *args, **kwargs):
        brokers = Broker.objects.filter(id__in=request.data['brokers']).all()
        symbol = get_object_or_404(Symbol, id=request.data['symbol'])
        limit_from = request.data['limit_from']
        limit_to = request.data['limit_to']
        order_type = request.data['type']
        coefficient = request.data['coefficient']
        if coefficient:
            rate = Rates.objects.filter(symbol=symbol).rate * coefficient
        else:
            rate = request.data['rate']
        user = get_object_or_404(User, id=request.data['user_id'])
        for broker in brokers:
            Order.objects.create(
                broker=broker, symbol=symbol, limit_from=limit_from,
                limit_to=limit_to, type=order_type, user=user,
                rate=rate, coefficient=coefficient
            )
        return Response(status=HTTP_204_NO_CONTENT)


class GenerateAccountView(APIView):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.data.get('user_id'))
        symbol = get_object_or_404(Symbol, id=request.data.get('symbol'))
        if Account.objects.filter(user=user, symbol=symbol).exists():
            raise ValidationError
        Account.objects.create(user=user, symbol=symbol, private_key=crypto_manager[symbol.name].generate_wallet())
        return Response(status=HTTP_204_NO_CONTENT)


class TextViewSet(ReadOnlyModelViewSet):
    serializer_class = TextSerializer
    queryset = Text.objects.all()
    lookup_field = 'name'
