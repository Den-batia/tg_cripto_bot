from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models


def random_string(symbols):
    return uuid4().hex[:symbols]


def random_ref_code():
    return random_string(16)


def random_order_id():
    return random_string(10)


def random_nickname():
    return random_string(10)


class User(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    referred_from = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, default=None, null=True)
    ref_code = models.CharField(default=random_ref_code, unique=True, max_length=16)
    nickname = models.CharField(default=random_nickname, unique=True, max_length=10)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['id']
    USERNAME_FIELD = 'telegram_id'

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


class Symbol(models.Model):
    name = models.CharField(max_length=4, unique=True)


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    balance = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    frozen = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT)
    private_key = models.CharField(max_length=128)
    earned_from_ref = models.DecimalField(max_digits=15, decimal_places=8, default=0)


class Broker(models.Model):
    name = models.CharField(max_length=32)


class Order(models.Model):
    id = models.CharField(primary_key=True, default=random_order_id, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='orders')
    limit_from = models.SmallIntegerField(validators=[MinValueValidator(1)])
    limit_to = models.SmallIntegerField(validators=[MinValueValidator(1)])
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.CharField(max_length=512, default='')
    type = models.CharField(max_length=3)


class Rates(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT, related_name='rates')


class Text(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField()
