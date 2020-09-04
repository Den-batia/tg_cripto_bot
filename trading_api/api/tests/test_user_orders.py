from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_405_METHOD_NOT_ALLOWED, HTTP_204_NO_CONTENT

from api.api import UserOrdersViewSet
from api.models import User, Broker, Symbol, Order, Rates
from api.tests.abstract_test import AbstractAPITestCase


class UserOrdersTest(AbstractAPITestCase):

    def _get_uri_detail(self, *args, **kwargs):
        return reverse('user-orders-detail', args, kwargs)

    def _get_uri_list(self, *args, **kwargs):
        return reverse('user-orders-list', args, kwargs)

    def setUp(self) -> None:
        super().setUp()
        self.view = UserOrdersViewSet.as_view({
            'post': 'create',
            'get': 'list',
            'delete': 'destroy',
            'patch': 'partial_update'
        })

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
        response = self._make_get_request(view=self.view, uri=self._get_uri_list(user_id=user.id), user_id=user.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data[0]['user'], user.nickname)

    def test_destroy(self):
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
        response = self._make_delete_request(view=self.view, uri=self._get_uri_detail(user_id=user.id, pk=order.id), user_id=user.id, pk=order.id)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.filter(id=order.id).get().is_deleted, True)


    def test_patch(self):
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        symbol = get_object_or_404(Symbol, name='eth')
        rate = Rates.objects.create(symbol=symbol, rate=3)
        order = Order.objects.create(broker=broker,
                                     limit_from=10,
                                     limit_to=10000,
                                     type='sell',
                                     user=user,
                                     symbol=symbol,
                                     rate=0.1,
                                     )
        data = {
            'limit_to': 200000,
            'limit_from': 80,
            'coefficient': 20
        }
        response = self._make_patch_request(data, uri=self._get_uri_detail(user_id=user.id, pk=order.id), user_id=user.id, pk=order.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['limit_from'], data['limit_from'])
        self.assertEqual(response.data['rate'], str(data['coefficient'] * Rates.objects.filter(symbol=symbol).get().rate))