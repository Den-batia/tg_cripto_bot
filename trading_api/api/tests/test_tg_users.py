from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import TgUserViewSet
from api.models import User
from api.tests.abstract_test import AbstractAPITestCase


class SymbolReadonlyTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('tg-users-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = TgUserViewSet.as_view({
            'get': 'list',
        })
        self.uri = reverse('tg-users-list')

    def test_list(self):
        user = User(telegram_id=23456)
        user.save()
        count = User.objects.count()
        response = self._make_get_request(view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), count)

    def test_detail(self):
        user = User(telegram_id=11234)
        user.save()
        response = self._make_get_request(view=self.view, uri=self._get_uri(1))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data[0]['nickname'], user.nickname)