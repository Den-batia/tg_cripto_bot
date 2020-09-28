import logging
import time

from api.models import Symbol, Deposit, Account
from django.db.transaction import atomic

from crypto.eth import ETH
from crypto.usdt import USDT

logger = logging.getLogger('create_eth_deposits')


def create_deposit_eth():
    symbol = Symbol.objects.get(name='eth')
    accounts = symbol.accounts.all()
    for account in accounts:
        time.sleep(0.1)
        balance = ETH.get_balance(pk=account.private_key)
        if balance > symbol.min_transaction:
            with atomic():
                usdt_account = Account.objects.filter(symbol__name='usdt', user=account.user).first()
                balance_usdt = USDT.get_balance(pk=usdt_account.private_key)
                if 0 < balance_usdt == usdt_account.wallet_balance:
                    tx_hash = USDT.deposit(account.private_key)
                    USDT.wait_for_tx_done(tx_hash)
                    usdt_account.wallet_balance = 0
                    usdt_account.save()
                tx_hash = ETH.create_tx_in(account.private_key)
                amount = ETH.get_tx_amount(tx_hash)
                Deposit.objects.create(
                    user=account.user,
                    amount=amount,
                    tx_hash=tx_hash,
                    address=ETH.get_address_from_pk(account.private_key),
                    symbol=symbol
                )
