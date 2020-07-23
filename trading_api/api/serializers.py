from rest_framework.fields import SerializerMethodField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from .models import User, Text, Symbol, Account, Order, Broker
from crypto.manager import crypto_manager


class WalletSerializer(ModelSerializer):
    class Meta:
        pass


class UserSerializer(ModelSerializer):
    invited_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'telegram_id', 'ref_code', 'invited_count')

    def get_invited_count(self, instance: User):
        return User.objects.filter(referred_from=instance).count()


class AccountSerializer(ModelSerializer):
    symbol = SlugRelatedField('name')
    address = SerializerMethodField()

    class Meta:
        model = Account
        fields = ('balance', 'frozen', 'earned_from_ref', 'address')

    def get_address(self, instance: Account):
        return crypto_manager[instance.symbol.name].get_address_from_pk(instance.private_key)


class UserAccountsSerializer(ModelSerializer):
    accounts = AccountSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'telegram_id', 'accounts')


class SymbolSerializer(ModelSerializer):
    class Meta:
        model = Symbol
        fields = ('id', 'name')


class OrderSerializer(ModelSerializer):
    broker = SlugRelatedField('name')
    user = SlugRelatedField('nickname')

    class Meta:
        model = Order
        fields = ('type', 'broker', 'rate', 'user', 'limit_from', 'limit_to', 'details')


class AggregatedOrderSerializer(ModelSerializer):
    orders = SerializerMethodField(read_only=True)

    class Meta:
        model = Broker
        fields = ('name', 'orders')

    def get_lots_cnt(self, instance: Broker):
        return instance.orders.filter(type=self.context['type'], symbol=self.context['symbol']).count()


class TextSerializer(ModelSerializer):
    class Meta:
        model = Text
        fields = ('text',)
