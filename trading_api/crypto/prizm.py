import requests
from decimal import Decimal
from os import environ as env


class PRIZM:
    """
    PK IS ADDRESS!
    """
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
    def _call(cls, method_name, query_string):
        return requests.get(f'{cls.URL}/prizm?requestType={method_name}{query_string}').json()

    @classmethod
    def _get_account(cls, sp):
        return cls._call('getAccountId', f'&secretPhrase={sp}')

    @classmethod
    def generate_wallet(cls, sp):
        return cls._get_account(sp)['account']

    @classmethod
    def is_address_valid(cls, address):
        return cls.RPC().validateaddress(address)['isvalid']

    @classmethod
    def get_address_from_pk(cls, pk):
        data = cls._call('getAccount', f'&account={pk}')
        return {'address': data['accountRS'], 'public_key': data['publicKey']}

    @classmethod
    def get_balance(cls, pk=None):
        if pk is None:
            pk = cls._get_account(sp=env['PRIZM_SP'])['account']
        res = cls._call('getAccount', f'&account={pk}')
        return cls.from_subunit(Decimal(res['balanceNQT']))

    @classmethod
    def get_transactions(cls, limit=30):
        return cls.RPC().listtransactions("*", limit)

    @classmethod
    def create_tx_out(cls, address, amount_btc, blocks_target=70):
        return cls.RPC().sendtoaddress(address, amount_btc, '', '', False, False, blocks_target)

    @classmethod
    def send_many(cls, venue: dict):
        return cls.RPC().sendmany("", venue)

    @classmethod
    def get_transaction_fee(cls, txid):
        try:
            tx = cls.RPC().gettransaction(txid)
            fee = abs(tx['fee'])
        except Exception:
            fee = None
        return fee

    @classmethod
    def get_link(cls, tx_hash):
        return cls.LINK + tx_hash
