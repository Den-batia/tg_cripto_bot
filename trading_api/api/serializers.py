from django.db.models import Q
from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from .models import User, Text, Symbol, Account, Order, Broker, Requisite, Deal
from crypto.manager import crypto_manager


class SymbolSerializer(ModelSerializer):
    class Meta:
        model = Symbol
        fields = ('id', 'name', 'min_withdraw', 'commission')


class BrokerSerializer(ModelSerializer):
    class Meta:
        model = Broker
        fields = ('id', 'name')


class UserSerializer(ModelSerializer):
    invited_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'telegram_id', 'ref_code', 'invited_count', 'is_admin', 'nickname', 'is_verify')

    def get_invited_count(self, instance: User):
        return User.objects.filter(referred_from=instance).count()


class AccountSerializer(ModelSerializer):
    symbol = SymbolSerializer(read_only=True)
    address = SerializerMethodField()

    class Meta:
        model = Account
        fields = ('balance', 'frozen', 'earned_from_ref', 'address', 'symbol')

    def get_address(self, instance: Account):
        return crypto_manager[instance.symbol.name].get_address_from_pk(instance.private_key)


class UserAccountsSerializer(ModelSerializer):
    accounts = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'telegram_id', 'accounts')

    def get_accounts(self, instance: User):
        return AccountSerializer(instance.accounts, many=True).data


class OrderSerializer(ModelSerializer):
    broker = SlugRelatedField('name', read_only=True)
    user = SlugRelatedField('nickname', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'type', 'broker', 'rate', 'user', 'limit_from', 'limit_to', 'details', 'is_active', 'coefficient')


class UserInfoSerializer(ModelSerializer):
    deals = SerializerMethodField(read_only=True)
    orders = SerializerMethodField(read_only=True)
    created_at = DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = User
        fields = ('id', 'nickname', 'is_verify', 'created_at', 'deals', 'orders')

    def get_deals(self, instance: User):
        return Deal.objects.filter((Q(buyer=instance) | Q(seller=instance)), status=3).count()

    def get_orders(self, instance: User):
        return instance.orders.filter(is_deleted=False).count()


class OrderDetailSerializer(ModelSerializer):
    broker = BrokerSerializer(read_only=True)
    user = UserInfoSerializer(read_only=True)
    symbol = SymbolSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'type', 'broker', 'rate', 'user', 'limit_from',
            'limit_to', 'details', 'symbol', 'is_active', 'is_deleted'
        )


class DealDetailSerializer(ModelSerializer):
    order = OrderDetailSerializer(read_only=True)
    buyer = UserInfoSerializer(read_only=True)
    seller = UserInfoSerializer(read_only=True)
    symbol = SymbolSerializer(read_only=True)

    class Meta:
        model = Deal
        fields = (
            'id', 'requisite', 'order', 'buyer', 'seller', 'rate',
            'status', 'amount_crypto', 'amount_currency', 'commission',
            'created_at', 'closed_at', 'symbol'
        )


class AggregatedOrderSerializer(ModelSerializer):
    orders_cnt = SerializerMethodField(read_only=True)

    class Meta:
        model = Broker
        fields = ('id', 'name', 'orders_cnt')

    def get_orders_cnt(self, instance: Broker):
        return instance.orders.filter(
            ~Q(user=self.context['ref']),
            type=self.context['type'],
            symbol=self.context['symbol'],
            is_deleted=False,
            is_active=True
        ).count()


class RequisiteSerializer(ModelSerializer):
    broker = BrokerSerializer(read_only=True)

    class Meta:
        model = Requisite
        fields = ('broker', 'requisite')


class TextSerializer(ModelSerializer):
    class Meta:
        model = Text
        fields = ('text',)
