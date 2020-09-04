import logging

from django.db.transaction import atomic

from crypto.btc import BTC
from utils.redis_queue import NotificationsQueue

from api.models import Symbol

logger = logging.getLogger('withdraw')


def withdraw():
    symbol = Symbol.objects.get(name='btc')
    to_withdraw = symbol.withdraws.filter(confirmed_at__isnull=True)
    to_withdraw_dict = {}
    with atomic():
        for withdraw_object in to_withdraw:
            account = withdraw_object.user.accounts.filter(symbol=withdraw_object.symbol).get()
            account.frozen -= (withdraw_object.amount + withdraw_object.commission_service)
            account.save()
            to_withdraw_dict[withdraw_object.address] = withdraw_object.amount
        if not to_withdraw_dict:
            return
        tx_hash = BTC.send_many(venue=to_withdraw_dict)
    commission_net = BTC.get_transaction_fee(tx_hash)
    for i, withdraw_object in enumerate(to_withdraw):
        if i == 0:
            withdraw_object.commission_blockchain = commission_net
        withdraw_object.tx_hash = tx_hash
        withdraw_object.save()
        NotificationsQueue.put(
            {
                'telegram_id': withdraw_object.user.telegram_id,
                'type': 'withdraw',
                'link': BTC.get_link(tx_hash)
            }
        )
