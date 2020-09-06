from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import SymbolsViewSet
from api.models import Symbol
from api.tests.abstract_test import AbstractAPITestCase


class SymbolListTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('symbol-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view_list = SymbolsViewSet.as_view({'get': 'list'})
        self.view_detail = SymbolsViewSet.as_view({'get': 'list'})
        self.uri = reverse('symbol-list')

    def test_list(self):
        count = Symbol.objects.count()
        response = self._make_get_request(view=self.view_list, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), count)

    def test_detail(self):
        response = self._make_get_request(view=self.view_detail, uri=self._get_uri(1))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'eth')
