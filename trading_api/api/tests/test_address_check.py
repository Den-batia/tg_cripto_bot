from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT

from api.api import AddressCheckView
from api.models import Account, User, Symbol
from crypto.manager import crypto_manager
from api.tests.abstract_test import AbstractAPITestCase


class AddressCheckTest(AbstractAPITestCase):

    def _get_uri(self, *args):
        return reverse('address-check', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = AddressCheckView.as_view()
        self.uri = reverse('address-check')

    def test_list(self):
        user = User(telegram_id=11234)
        user.save()
        symbol = get_object_or_404(Symbol, name='eth')
        account = Account(user=user, symbol=symbol, private_key='0x1111111111111111111111111111111111111111111111111111111111111111')
        account.save()
        address = crypto_manager[symbol.name].get_address_from_pk(account.private_key)
        data = {
            'symbol': symbol.id,
            'address': address,
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.data['is_valid'], True)
