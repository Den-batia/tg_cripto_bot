from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import SymbolsViewSet
from api.models import Symbol
from api.tests.abstract_test import AbstractAPITestCase


<<<<<<< HEAD
class SymbolListTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('symbol-detail', args)
=======
class SymbolReadonlyTest(AbstractAPITestCase):
    def _get_uri(self, **kwargs):
        return reverse('symbol-detail', **kwargs)
>>>>>>> master

    def setUp(self) -> None:
        super().setUp()
        self.view_list = SymbolsViewSet.as_view({'get': 'list'})
<<<<<<< HEAD
        self.view_detail = SymbolsViewSet.as_view({'get': 'list'})
=======
        self.view_detail = SymbolsViewSet.as_view({'get': 'detail'})
>>>>>>> master
        self.uri = reverse('symbol-list')

    def test_list(self):
        count = Symbol.objects.count()
<<<<<<< HEAD
        response = self._make_get_request(view=self.view_list, uri=self.uri)
=======
        response = self._make_get_request(view=self.view_list, uri=self.view_list)
>>>>>>> master
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), count)

    def test_detail(self):
<<<<<<< HEAD
        response = self._make_get_request(view=self.view_detail, uri=self._get_uri(1))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'eth')
=======
        response = self._make_get_request(view=self.view_detail, uri=self._get_uri(id=1))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['name'], 'eth')
>>>>>>> master
