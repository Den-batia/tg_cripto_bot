import requests
from decimal import Decimal
from os import environ as env


class PRIZM:
    URL = env['PRIZM_NODE']
    LINK = "https://prizmexplorer.com/tx/"
    DECIMALS = 2

    @classmethod
    def from_subunit(cls, val: Decimal):
        return val / Decimal(100)

    @classmethod
    def to_subunit(cls, val: Decimal):
        return val * Decimal(100)

    @classmethod
    def _call(cls, method_name, query_string, method='get'):
        return getattr(requests, method)(f'{cls.URL}/prizm?requestType={method_name}{query_string}').json()

    @classmethod
    def _get_account(cls, sp=None, pk=None):
        if sp is not None:
            return cls._call('getAccountId', f'&secretPhrase={sp}')
        elif pk is not None:
            return cls._call('getAccountId', f'&publicKey={pk}')

    @classmethod
    def generate_wallet(cls, sp):
        return cls._get_account(sp)['publicKey']

    @classmethod
    def is_address_valid(cls, address):
        return True

    @classmethod
    def get_address_from_pk(cls, pk):
        data = cls._get_account(pk=pk)
        return {'address': data['accountRS'], 'public_key': data['publicKey']}

    @classmethod
    def _get_system_account(cls):
        return cls._get_account(sp=env['PRIZM_SP'])

    @classmethod
    def get_balance(cls, pk=None):
        if pk is None:
            pk = cls._get_system_account()['account']
        res = cls._call('getAccount', f'&account={pk}')
        return cls.from_subunit(Decimal(res.get('balanceNQT', 0)))

    @classmethod
    def get_link(cls, tx_hash):
        return cls.LINK + tx_hash

    @classmethod
    def get_transaction_fee(cls, *args):
        return Decimal('20')

    @classmethod
    def send_tx(cls, sp, recipient, amount, fee):
        amount = cls.to_subunit(amount)
        fee = cls.to_subunit(fee)
        resp = cls._call(
            'sendMoney',
            f'&secretPhrase={sp}&recipient={recipient}&amountNQT={amount}&deadline=1&feeNQT={fee}',
            method='post'
        )
        print(resp)
        if resp.get('broadcasted'):
            return resp['fullHash']

    @classmethod
    def send_tx_in(cls, sp, amount):
        fee = cls.get_transaction_fee()
        return cls.send_tx(sp, recipient=cls._get_system_account()['accountRS'], amount=amount-fee, fee=fee)
