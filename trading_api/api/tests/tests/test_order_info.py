from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK

from api.api import OrderInfoViewSet
from api.models import User, Broker, Symbol, Order
from api.tests.abstract_test import AbstractAPITestCase


class OrderInfoTest(AbstractAPITestCase):
    def _get_uri(self, *args):
        return reverse('order-info-detail', args)

    def setUp(self) -> None:
        super().setUp()
        self.view = OrderInfoViewSet.as_view({'get': 'retrieve'})

    def test_list(self):
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        symbol = get_object_or_404(Symbol, name='eth')
        order = Order.objects.create(broker=broker,
                                     limit_from=10,
                                     limit_to=10000,
                                     type='sell',
                                     user=user,
                                     symbol=symbol,
                                     rate=0.1)
        response = self._make_get_request(view=self.view, uri=self._get_uri(order.id,), pk=order.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)