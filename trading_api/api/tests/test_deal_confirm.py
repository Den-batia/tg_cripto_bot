from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from api.api import ConfirmDealView
from api.models import Account, User, Symbol, Broker, Order, Requisite, Deal
from api.tests.abstract_test import AbstractAPITestCase
from unittest.mock import patch

from crypto.manager import crypto_manager


class DealConfirmTest(AbstractAPITestCase):

    def _get_uri(self, *args, **kwargs):
        return reverse('confirm-deal', args, kwargs)

    def setUp(self) -> None:
        super().setUp()
        self.view = ConfirmDealView.as_view()

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_list(self, put):
        buyer = User.objects.create(telegram_id=2345)
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
        deal = Deal.objects.create(
            seller=user, buyer=buyer, order=order, rate=1, requisite=requisite,
            amount_crypto=1, amount_currency=1, symbol=symbol)
        data = {
            'ref': user.id
        }
        response = self._make_post_request(data, view=self.view, uri=self._get_uri(deal_id=deal.id), deal_id=deal.id)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Deal.objects.filter(id=deal.id).get().status, 1)

    @patch('utils.redis_queue.NotificationsQueue.put')
    def test_status_(self, put):
        buyer = User.objects.create(telegram_id=2345)
        user = User.objects.create(telegram_id=23456)
        broker = Broker.objects.create(name='Банковский перевод внутри страны')
        symbol = get_object_or_404(Symbol, name='eth')
        requisite = Requisite.objects.create(user=user, broker=broker, requisite='заливать лаве сюда => 1234....1345')
        account = Account.objects.create(user=user,
                                         symbol=symbol,
                                         private_key='private_key',
                                         balance=10)

        order = Order.objects.create(broker=broker,
                                     limit_from=10,
                                     limit_to=10000,
                                     type='sell',
                                     user=user,
                                     symbol=symbol,
                                     rate=0.1)
        deal = Deal.objects.create(
            seller=user, buyer=buyer, order=order, rate=1, requisite=requisite,
            amount_crypto=1, amount_currency=1, symbol=symbol, status=2)
        data = {
            'ref': user.id
        }
        response = self._make_post_request(data, view=self.view, uri=self._get_uri(deal_id=deal.id), deal_id=deal.id)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

