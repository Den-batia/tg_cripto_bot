import logging
import time
from datetime import timezone, datetime
from decimal import Decimal

from api.models import Symbol
from crypto.prizm import PRIZM
from django.db.transaction import atomic

from utils.redis_queue import NotificationsQueue

from api.models import Deposit

logger = logging.getLogger('prizm_deposits')


UID_ACCOUNT_MAPPING = {}


def _get_account(user_id):
    account = UID_ACCOUNT_MAPPING.get(user_id)
    if account is None:
        account = PRIZM._get_account(sp=user_id)['account']
        UID_ACCOUNT_MAPPING[user_id] = account
    return account


def deposit_prizm():
    symbol = Symbol.objects.get(name='prizm')
    accounts = symbol.accounts.all()
    for account in accounts:
        account_id = _get_account(account.user_id)
        balance = Decimal(PRIZM.get_balance(pk=account_id))
        if balance > 0:
            with atomic():
                tx_hash = PRIZM.send_tx_in(sp=account.user_id, amount=balance)
                if tx_hash:
                    account.balance += balance
                    account.save()
                    dep = Deposit.objects.create(
                        user_id=account.user_id,
                        amount=balance,
                        address=PRIZM._get_system_account()['address'],
                        symbol=symbol,
                        confirmed_at=datetime.now(timezone.utc),
                        tx_hash=tx_hash
                    )
                    NotificationsQueue.put({'telegram_id': dep.user.telegram_id, 'type': 'deposit',
                                            'amount': dep.amount, 'symbol': symbol.name})

