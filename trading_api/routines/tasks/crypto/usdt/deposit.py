import logging
import time
from datetime import timezone, datetime

from api.models import Symbol
from crypto.eth import ETH
from crypto.usdt import USDT
from django.db.transaction import atomic

from utils.redis_queue import NotificationsQueue

from api.models import Deposit

logger = logging.getLogger('usdt_deposits')


def deposit():
    symbol = Symbol.objects.get(name='usdt')
    accounts = symbol.accounts.all()
    for account in accounts:
        time.sleep(0.1)
        balance_usdt = USDT.get_balance(pk=account.private_key)
        if balance_usdt > account.wallet_balance:
            with atomic():
                amount = balance_usdt - account.wallet_balance
                account.wallet_balance = balance_usdt
                account.balance += amount
                account.save()
                dep = Deposit.objects.create(
                    user=account.user,
                    amount=amount,
                    address=ETH.get_address_from_pk(account.private_key),
                    symbol=symbol,
                    confirmed_at=datetime.now(timezone.utc)
                )
                NotificationsQueue.put({'telegram_id': dep.user.telegram_id, 'type': 'deposit',
                                        'amount': dep.amount, 'symbol': symbol.name})

