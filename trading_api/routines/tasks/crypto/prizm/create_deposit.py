import logging
import time
from decimal import Decimal

from api.models import Symbol, Deposit
from crypto.prizm import PRIZM

logger = logging.getLogger('prizm_deposits')


UID_ACCOUNT_MAPPING = {}


def _get_account(user_id):
    account = UID_ACCOUNT_MAPPING.get(user_id)
    if account is None:
        account = PRIZM._get_account(sp=user_id)['account']
        UID_ACCOUNT_MAPPING[user_id] = account
    return account


def create_deposit_prizm():
    symbol = Symbol.objects.get(name='prizm')
    accounts = symbol.accounts.all()
    for account in accounts:
        account_id = _get_account(account.user_id)
        balance = Decimal(PRIZM.get_balance(pk=account_id))
        if balance > symbol.min_transaction:
            print(account.user.nickname, balance)
            tx_hash = PRIZM.send_tx_in(sp=account.user_id, amount=balance)
            if tx_hash:
                Deposit.objects.create(
                    user_id=account.user_id,
                    amount=balance,
                    address=PRIZM._get_system_account()['accountRS'],
                    symbol=symbol,
                    tx_hash=tx_hash
                )
        time.sleep(0.5)
