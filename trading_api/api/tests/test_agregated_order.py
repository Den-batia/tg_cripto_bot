from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import AggregatedOrderView
from api.models import User, Broker, Symbol, Rates, Order
from api.tests.abstract_test import AbstractAPITestCase


class AgregatedOrderTest(AbstractAPITestCase):

    def _get_uri(self, *args):
        return reverse('aggregated-orders', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = AggregatedOrderView.as_view()
        self.uri = reverse('aggregated-orders')

    def test_list(self):
        symbol = get_object_or_404(Symbol, name='eth')
        user = User.objects.create(telegram_id=23456)
        data ={
            'type': 1,
            'symbol': symbol.id,
            'ref': user.id
        }
        response = self._make_get_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), len(Broker.objects.all()))

