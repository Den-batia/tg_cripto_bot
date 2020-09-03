from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import UserAccountsViewSet
from api.models import User, Symbol, Account
from crypto.manager import crypto_manager
from api.tests.abstract_test import AbstractAPITestCase


class SymbolReadonlyTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('accounts-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = UserAccountsViewSet.as_view({
            'get': 'retrieve',
        })

    def test_detail(self):
        user = User(telegram_id=11234)
        user.save()
        symbol = get_object_or_404(Symbol, name='eth')
        account = Account(user=user, symbol=symbol, private_key=crypto_manager[symbol.name].generate_wallet())
        account.save()

        response = self._make_get_request(view=self.view, uri=self._get_uri(user.id), pk=user.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['telegram_id'], user.telegram_id)
        self.assertGreaterEqual(len(response.data['accounts']), 0)
        print(response.data)