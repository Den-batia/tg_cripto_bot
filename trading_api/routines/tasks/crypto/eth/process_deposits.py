import logging
from datetime import timezone, datetime

from api.models import Symbol, Deposit
from django.db.transaction import atomic

from crypto.eth import ETH
from utils.redis_queue import NotificationsQueue

logger = logging.getLogger('process_eth_deposits')


def process():
    symbol = Symbol.objects.get()
    for dep in Deposit.objects.filter(confirmed_at__isnull=True, symbol=symbol):
        if ETH.is_transaction_delivered(dep.tx_hash):
            with atomic():
                dep.confirmed_at = datetime.now(timezone.utc)
                acc = dep.user.accounts.filter(symbol=symbol).first()
                acc.balance += dep.amount
                acc.save()
                dep.save()
                NotificationsQueue.put({'telegram_id': dep.user.telegram_id, 'type': 'dep', 'amount': dep.amount, 'symbol': symbol.name})
