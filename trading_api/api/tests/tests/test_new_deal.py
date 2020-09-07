from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from api.api import NewDealView
from api.models import Account, User, Symbol, Broker, Order, Requisite
from api.tests.abstract_test import AbstractAPITestCase
from unittest.mock import patch

from crypto.manager import crypto_manager


class NewDealTest(AbstractAPITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.view = NewDealView.as_view()
        self.uri = reverse('new-deal')

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_list(self, put):
        bayer = User.objects.create(telegram_id=2345)
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        symbol = get_object_or_404(Symbol, name='eth')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='заливать лаве сюда => 1234....1345')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key=crypto_manager[symbol.name].generate_wallet(),
                                         balance=10)

        order = Order.objects.create(broker=broker,
                                     limit_from=10,
                                     limit_to=10000,
                                     type='sell',
                                     user=user,
                                     symbol=symbol,
                                     rate=0.1)
        data = {
            'amount_crypto': 1,
            'amount': 1,
            'order_id': order.id,
            'rate': 1,
            'requisite': 'qwe',
            'seller_id': user.id,
            'buyer_id': bayer.id,
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['seller']['nickname'], user.nickname)
        self.assertEqual(response.data['requisite'], data['requisite'])

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_zero_balance(self, put):
        bayer = User.objects.create(telegram_id=2345)
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        symbol = get_object_or_404(Symbol, name='eth')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='заливать лаве сюда => 1234....1345')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key=crypto_manager[symbol.name].generate_wallet(),
                                         )

        order = Order.objects.create(broker=broker,
                                     limit_from=10,
                                     limit_to=10000,
                                     type='sell',
                                     user=user,
                                     symbol=symbol,
                                     rate=0.1)
        data = {
            'amount_crypto': 1,
            'amount': 1,
            'order_id': order.id,
            'rate': 1,
            'requisite': 'qwe',
            'seller_id': user.id,
            'buyer_id': bayer.id,
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.exception, True)

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_account_is_deleted(self, put):
        bayer = User.objects.create(telegram_id=2345)
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        symbol = get_object_or_404(Symbol, name='eth')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='заливать лаве сюда => 1234....1345')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key=crypto_manager[symbol.name].generate_wallet(),
                                         balance=10
                                         )

        order = Order.objects.create(broker=broker,
                                     limit_from=10,
                                     limit_to=10000,
                                     type='sell',
                                     user=user,
                                     symbol=symbol,
                                     rate=0.1,
                                     is_deleted=True)
        data = {
            'amount_crypto': 1,
            'amount': 1,
            'order_id': order.id,
            'rate': 1,
            'requisite': 'qwe',
            'seller_id': user.id,
            'buyer_id': bayer.id,
        }
        response = self._make_post_request(data, view=self.view, uri=self.uri)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)