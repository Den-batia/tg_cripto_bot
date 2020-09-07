from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT

from api.api import NewOrderView
from api.models import User, Broker, Symbol, Rates, Order
from api.tests.abstract_test import AbstractAPITestCase


class NewOrderTest(AbstractAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.view = NewOrderView.as_view()
        self.uri = reverse('new-order')

    def test_list(self):
        user = User.objects.create(telegram_id=23456)
        brocker_1 = Broker.objects.create(name='Банковский перевод внутри страны')
        brocker_2 = Broker.objects.create(name='Тинькофф')
        symbol = get_object_or_404(Symbol, name='eth')
        data = {
            'brokers': [brocker_1.id, brocker_2.id],
            'limit_from': 10,
            'limit_to': 1000000,
            'type': 'sell',
            'user_id': user.id,
            'symbol': symbol.id,
            'rate': 0.1,
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 2)
