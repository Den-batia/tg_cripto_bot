from .btc import BTC
from .eth import ETH
from .prizm import PRIZM
from .usdt import USDT


class Manager:
    def __init__(self):
        self.currencies = {
            'btc': BTC,
            'eth': ETH,
            'usdt': USDT,
            'prizm': PRIZM
        }

    def __getitem__(self, item):
        return self.currencies[item]

    def get_address_from_pk(self, symbol, pk):
        f = getattr(self.currencies[symbol], 'get_address_from_pk')
        return f(pk)

    def get_balance(self, symbol, pk):
        f = getattr(self.currencies[symbol], 'get_balance')
        return f(pk)

    def generate_wallet(self, symbol):
        f = getattr(self.currencies[symbol], 'generate_wallet')
        return f()

    def is_address_valid(self, symbol, address):
        f = getattr(self.currencies[symbol], 'is_address_valid')
        return f(address)

    def get_link(self, symbol, tx_hash):
        f = getattr(self.currencies[symbol], 'get_link')
        return f(tx_hash)


crypto_manager = Manager()
