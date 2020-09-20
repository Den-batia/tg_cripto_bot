from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models


def random_string(symbols):
    return uuid4().hex[:symbols]


def random_ref_code():
    return random_string(16)


def random_order_id():
    return random_string(10)


def random_deal_id():
    return random_string(15)


def random_nickname():
    return random_string(10)


class User(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    referred_from = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, default=None, null=True)
    ref_part = models.DecimalField(max_digits=6, decimal_places=3, default=0.3)
    ref_code = models.CharField(default=random_ref_code, unique=True, max_length=16)
    nickname = models.CharField(default=random_nickname, unique=True, max_length=10)
    is_admin = models.BooleanField(default=False)
    is_verify = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_nickname_change = models.DateTimeField(blank=True, null=True, default=None)

    REQUIRED_FIELDS = ['id']
    USERNAME_FIELD = 'telegram_id'

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


class Symbol(models.Model):
    name = models.CharField(max_length=5, unique=True)
    min_transaction = models.DecimalField(max_digits=15, decimal_places=8, default='0.01')
    commission = models.DecimalField(max_digits=15, decimal_places=8, default='0.005')
    deals_commission = models.DecimalField(max_digits=5, decimal_places=5, default=0.001)


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    balance = models.DecimalField(max_digits=15, decimal_places=8, default=0, validators=[MinValueValidator(0)])
    frozen = models.DecimalField(max_digits=15, decimal_places=8, default=0, validators=[MinValueValidator(0)])
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT, related_name='accounts')
    private_key = models.CharField(max_length=128)
    earned_from_ref = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    wallet_balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)


class Broker(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)


class Order(models.Model):
    id = models.CharField(primary_key=True, default=random_order_id, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT, related_name='orders')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='orders')
    limit_from = models.IntegerField(validators=[MinValueValidator(1)])
    limit_to = models.IntegerField(validators=[MinValueValidator(1)])
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    details = models.CharField(max_length=512, default='')
    type = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_system_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


class Requisite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisites')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='requisites')
    requisite = models.CharField(max_length=128)

    class Meta:
        unique_together = ('user', 'broker')


class Deal(models.Model):
    id = models.CharField(primary_key=True, default=random_deal_id, max_length=15)
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT, related_name='deals')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='deals')
    requisite = models.CharField(max_length=128, blank=True, default='')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.SmallIntegerField(default=0)
    amount_crypto = models.DecimalField(max_digits=15, decimal_places=8)
    amount_currency = models.DecimalField(max_digits=15, decimal_places=2)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_deals')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_deals')
    commission = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True, default=None)


class Dispute(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name='dispute')
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes')
    created_at = models.DateTimeField(auto_now_add=True)


class UserRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField()
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='rates')

    class Meta:
        unique_together = ('user', 'target', 'deal')


class Deposit(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name='deposits')
    tx_hash = models.CharField(max_length=66, default=None, null=True)
    address = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(default=None, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=8)


class Withdraw(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdraws')
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name='withdraws')
    tx_hash = models.CharField(max_length=66, default=None, null=True)
    address = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(default=None, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    commission_service = models.DecimalField(max_digits=15, decimal_places=8)
    commission_blockchain = models.DecimalField(max_digits=15, decimal_places=8, default=0)


class Rates(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT, related_name='rates')


class Text(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField()
