import logging
from datetime import timezone, datetime

from django.db.transaction import atomic

from crypto.btc import BTC
from utils.redis_queue import NotificationsQueue

from api.models import Symbol

from api.api import BalanceManagementMixin

logger = logging.getLogger('withdraw')


def withdraw():
    symbol = Symbol.objects.get(name='btc')
    to_withdraw = symbol.withdraws.filter(confirmed_at__isnull=True)
    to_withdraw_dict = {}
    bm = BalanceManagementMixin()
    with atomic():
        for withdraw_object in to_withdraw:
            bm.add_frozen(
                -(withdraw_object.amount + withdraw_object.commission_service),
                withdraw_object.user,
                symbol
            )
            withdraw_object.confirmed_at = datetime.now(timezone.utc)
            withdraw_object.save()
            to_withdraw_dict[withdraw_object.address] = withdraw_object.amount
        if not to_withdraw_dict:
            return
        tx_hash = BTC.send_many(venue=to_withdraw_dict)
    commission_net = BTC.get_transaction_fee(tx_hash)
    total_commission = -commission_net
    for i, withdraw_object in enumerate(to_withdraw):
        total_commission += withdraw_object.commission_service
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

    bm.add_commission(total_commission, symbol)
