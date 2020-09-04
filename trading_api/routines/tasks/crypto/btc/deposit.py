import logging
from datetime import timezone, datetime
from decimal import Decimal

from django.db.transaction import atomic

from api.models import Account, Deposit, Symbol
from crypto.btc import BTC

from utils.redis_queue import NotificationsQueue

from api.api import BalanceManagementMixin

logger = logging.getLogger('deposit')


def process_deposit():
    all_deposit_transactions = filter(lambda item: item['category'] == 'receive', BTC.get_transactions())
    symbol = Symbol.objects.get(name='btc')
    bm = BalanceManagementMixin()
    for tx in all_deposit_transactions:
        if tx['confirmations'] > 0 and not Deposit.objects.filter(tx_hash=tx['txid'], address=tx['address']).exists():
            account = Account.objects.filter(private_key=tx['address']).first()
            if account:
                with atomic():
                    now = datetime.now(timezone.utc)
                    dep = Deposit.objects.create(
                        tx_hash=tx['txid'],
                        user=account.user,
                        created_at=now,
                        confirmed_at=now,
                        amount=tx['amount'],
                        symbol=symbol,
                        address=tx['address']
                    )
                    bm.add_balance(Decimal(tx['amount']), account.user, symbol)
                    NotificationsQueue.put(
                        {
                            'telegram_id': dep.user.telegram_id,
                            'type': 'deposit',
                            'amount': dep.amount,
                            'symbol': dep.symbol.name
                        }
                    )
