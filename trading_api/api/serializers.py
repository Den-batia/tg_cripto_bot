from rest_framework.fields import SerializerMethodField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from .models import User, Text, Symbol, Account, Order, Broker
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
        fields = ('id', 'telegram_id', 'ref_code', 'invited_count')

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
        fields = ('type', 'broker', 'rate', 'user', 'limit_from', 'limit_to', 'details')


class AggregatedOrderSerializer(ModelSerializer):
    orders_cnt = SerializerMethodField(read_only=True)

    class Meta:
        model = Broker
        fields = ('id', 'name', 'orders_cnt')

    def get_orders_cnt(self, instance: Broker):
        return instance.orders.filter(type=self.context['type'], symbol=self.context['symbol'], is_deleted=False).count()


class TextSerializer(ModelSerializer):
    class Meta:
        model = Text
        fields = ('text',)
