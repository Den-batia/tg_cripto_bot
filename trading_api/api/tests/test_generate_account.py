from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT

from api.api import GenerateAccountView
from api.models import Account, User, Symbol
from api.tests.abstract_test import AbstractAPITestCase


class GenerateAccountTest(AbstractAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.view = GenerateAccountView.as_view()
        self.uri = reverse('generate-account')

    def test_list(self):
        user = User(telegram_id=1234)
        user.save()
        symbol = get_object_or_404(Symbol, name='eth')
        data = {
            'user_id': user.id,
            'symbol': symbol.id
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.count(), 1)


