from uuid import uuid4

from django.db import models

from django.db import models


def random_string():
    return uuid4().hex[:16]


class User(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    referred_from = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, default=None, null=True)
    ref_code = models.CharField(default=random_string, unique=True, max_length=16)
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
    name = models.CharField()


class Wallet(models.Model):
    pass


class Rates(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    symbol = models.ForeignKey(Symbol, on_delete=models.PROTECT, related_name='rates')


class Text(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField()
