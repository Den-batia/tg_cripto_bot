import logging
from datetime import timezone, datetime

from django.db.transaction import atomic

from crypto.prizm import PRIZM
from utils.redis_queue import NotificationsQueue

from api.models import Symbol

from api.api import BalanceManagementMixin

logger = logging.getLogger('withdraw')


def withdraw():
    symbol = Symbol.objects.get(name='prizm')
    to_withdraw = symbol.withdraws.filter(confirmed_at__isnull=True)
    bm = BalanceManagementMixin()
    with atomic():
        for withdraw_object in to_withdraw:
            bm.add_frozen(
                -(withdraw_object.amount + withdraw_object.commission_service),
                withdraw_object.user,
                symbol
            )
            tx_hash = PRIZM.send_tx(
                amount=withdraw_object.amount,
                recipient=withdraw_object.address,
                sp=withdraw_object.user_id
            )
            if tx_hash:
                commission_net = PRIZM.get_commission()

                withdraw_object.confirmed_at = datetime.now(timezone.utc)
                withdraw_object.commission_blockchain = commission_net
                withdraw_object.tx_hash = tx_hash
                withdraw_object.save()

                NotificationsQueue.put(
                    {
                        'telegram_id': withdraw_object.user.telegram_id,
                        'type': 'withdraw',
                        'link': PRIZM.get_link(tx_hash)
                    }
                )

                bm.add_commission(withdraw_object.commission_service - commission_net, symbol)
