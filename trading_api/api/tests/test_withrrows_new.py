from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from api.api import NewWithdrawView
from api.models import Account, User, Symbol, Broker, Order, Requisite, Deal
from api.tests.abstract_test import AbstractAPITestCase



class NewWithdrawTest(AbstractAPITestCase):

    def _get_uri(self, *args, **kwargs):
        return reverse('new-withdraw', args, kwargs)

    def setUp(self) -> None:
        super().setUp()
        self.view = NewWithdrawView.as_view()
        self.uri = reverse('new-withdraw')

    def test_balance_not_0(self):
        user = User.objects.create(telegram_id=23456)
        symbol = get_object_or_404(Symbol, name='eth')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key='private_key',
                                         balance=10)

        data = {
            'symbol': symbol.id,
            'user_id': user.id,
            'address': '0x55d96d2efccb87d76c13b279e24603ce053260b6',
            'amount': 0.1,

        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(float(user.accounts.filter(symbol=symbol).get().balance), account.balance - data['amount'] - float(symbol.commission))


    def test_balance_is_0(self):
        user = User.objects.create(telegram_id=23456)
        symbol = get_object_or_404(Symbol, name='eth')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key='private_key',
                                         )

        data = {
            'symbol': symbol.id,
            'user_id': user.id,
            'address': '0x55d96d2efccb87d76c13b279e24603ce053260b6',
            'amount': 0.1,

        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_invalid_address(self):
        user = User.objects.create(telegram_id=23456)
        symbol = get_object_or_404(Symbol, name='eth')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key='private_key',
                                         balance=10)

        data = {
            'symbol': symbol.id,
            'user_id': user.id,
            'address': '0x55d96d2efcqq87d76c13b279e24603ce053260b6',
            'amount': 0.1,

        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)