import logging
from datetime import datetime, timezone

from django.db.transaction import atomic
from utils.redis_queue import NotificationsQueue
from api.models import Symbol
from crypto.prizm import PRIZM

logger = logging.getLogger('prizm_deposits')


def process_deposit_prizm():
    symbol = Symbol.objects.get(name='prizm')
    for dep in symbol.deposits.filter(confirmed_at__isnull=True):
        tx = PRIZM.get_tx(dep.tx_hash)
        print(tx)
        if tx['confirmations'] > 0:
            with atomic():
                account = dep.user.accounts.filter(symbol=symbol).first()
                account.balance += dep.amount
                dep.confirmed_at = datetime.now(timezone.utc)
                dep.save()
                account.save()
            NotificationsQueue.put(
                {
                    'telegram_id': dep.user.telegram_id,
                    'type': 'deposit',
                    'amount': dep.amount,
                    'symbol': symbol.name
                }
            )

