import logging

from api.models import Symbol, Deposit
from django.db.transaction import atomic

from crypto.eth import ETH

logger = logging.getLogger('create_eth_deposits')


def create():
    symbol = Symbol.objects.get(name='eth')
    accounts = symbol.accounts.all()
    for account in accounts:
        balance = ETH.get_balance(pk=account.private_key)
        if balance > 0.01:
            with atomic():
                tx_hash = ETH.create_tx_in(account.private_key)
                amount = ETH.get_tx_amount(tx_hash)
                Deposit.objects.create(user=account.user, amount=amount, tx_hash=tx_hash, symbol=symbol)

