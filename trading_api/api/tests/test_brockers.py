from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import BrokersViewSet
from api.models import Symbol, Broker
from api.tests.abstract_test import AbstractAPITestCase


class BrokersTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('brokers-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = BrokersViewSet.as_view({'get': 'list'})
        self.uri = reverse('brokers-list')

    def test_list(self):
        broker = Broker.objects.create(name='Мой банк')
        response = self._make_get_request(view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Broker.objects.get(name=broker.name).id, broker.id)
