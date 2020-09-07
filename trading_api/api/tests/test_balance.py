from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from django.db.models import Q, Sum
from api.api import BalanceView
from api.models import User, Symbol, Account
from api.tests.abstract_test import AbstractAPITestCase

class BalanceTest(AbstractAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.view = BalanceView.as_view()
        self.uri = reverse('balance')

    def test_get(self):
        user = User.objects.create(telegram_id=23456)
        user_1 = User.objects.create(telegram_id=2456)
        symbol = get_object_or_404(Symbol, name='eth')
        account = Account.objects.create(user=user, symbol=symbol, private_key='private_key')
        account_1 = Account.objects.create(user=user_1, symbol=symbol, private_key='private_key')
