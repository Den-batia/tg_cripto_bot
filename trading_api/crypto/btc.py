from decimal import Decimal
from os import environ as env

from bitcoinrpc.authproxy import AuthServiceProxy


class BTC:
    """
    PK IS ADDRESS!
    """
    RPC = lambda: AuthServiceProxy(env['BTC_NODE'])
    LINK = 'https://live.blockcypher.com/btc-testnet/tx/' if env.get('TEST') else "https://www.blockchain.com/btc/tx/"
    DECIMALS = 8

    @classmethod
    def _get_new_address(cls):
        return cls.RPC().getnewaddress()

    @classmethod
    def generate_wallet(cls):
        return cls._get_new_address()

    @classmethod
    def is_address_valid(cls, address):
        return cls.RPC().validateaddress(address)['isvalid']

    @classmethod
    def get_address_from_pk(cls, pk):
        return pk

    @classmethod
    def get_balance(cls):
        res = cls.RPC().getbalance()
        return Decimal(res)

    @classmethod
    def get_node_balance(cls, confirmations=0):
        return cls.RPC().getbalance("*", confirmations)

    @classmethod
    def get_total_received(cls, address=None):
        return cls.RPC().getreceivedbyaddress(address, 1)

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
