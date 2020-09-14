import time

import requests
from web3 import Web3, HTTPProvider
from os import environ as env


if env.get('TEST'):
    web3 = Web3(HTTPProvider('https://ropsten.infura.io/v3/6ebd1c9c66c445eeb9715eb27eab7f60'))
    chain = 3
else:
    web3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/f413f73cb5dd41cfa4251127c4078bf4'))
    chain = 1


gas = 21000


class ETH:
    PK = env.get('ETH_PK')

    @classmethod
    def generate_wallet(cls):
        return web3.eth.account.create().privateKey.hex()

    @classmethod
    def from_subunit(cls, val):
        sign = 1
        if val < 0:
            val = abs(val)
            sign = -1
        return sign * web3.fromWei(val, 'ether')

    @classmethod
    def to_subunit(cls, val):
        sign = 1
        if val < 0:
            val = abs(val)
            sign = -1
        return sign * web3.toWei(val, 'ether')

    @classmethod
    def is_address_valid(cls, address):
        return web3.isAddress(address.lower())

    @classmethod
    def get_address_from_pk(cls, pk):
        return web3.eth.account.privateKeyToAccount(pk).address

    @classmethod
    def get_balance(cls, pk=None):
        if pk is not None:
            address = cls.get_address_from_pk(pk)
        else:
            address = cls.get_address_from_pk(cls.PK)

        return cls.from_subunit(web3.eth.getBalance(address))

    @classmethod
    def get_gas_price(cls):
        url = 'https://api.etherscan.io/api?module=gastracker&action=gasoracle'
        gas_price = int(requests.get(url).json()['result']['FastGasPrice'])
        if gas_price > 1000:
            gas_price = 1000
        return gas_price

    @classmethod
    def get_net_commission(cls, gwei):
        gas_price = web3.toWei(gwei, 'gwei')
        return cls.from_subunit(gas * gas_price)

    @classmethod
    def _create_tx(cls, amount, to, from_address, gwei, subtract_fee):
        gas_price = web3.toWei(gwei, 'gwei')
        amount = cls.to_subunit(amount)
        if subtract_fee:
            amount = amount - gas * gas_price

        transaction = {
            'to': to,
            'value': int(amount),
            'gas': int(gas),
            'gasPrice': gas_price,
            'nonce': web3.eth.getTransactionCount(from_address),
            'chainId': chain
        }
        return transaction

    @classmethod
    def create_tx_out(cls, address, amount, gwei):
        account = web3.eth.account.privateKeyToAccount(cls.PK)
        to = web3.toChecksumAddress(address)
        tx = cls._create_tx(amount=amount, to=to, from_address=account.address, gwei=gwei, subtract_fee=False)
        signed_txn = web3.eth.account.signTransaction(tx, private_key=cls.PK)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return tx_hash.hex()

    @classmethod
    def create_tx_in(cls, pk):
        balance = cls.get_balance(pk=pk)
        system_address = web3.eth.account.privateKeyToAccount(cls.PK).address
        from_address = web3.eth.account.privateKeyToAccount(pk).address
        tx = cls._create_tx(
            amount=balance, to=system_address,
            from_address=from_address, gwei=cls.get_gas_price(), subtract_fee=True
        )
        signed_txn = web3.eth.account.signTransaction(tx, private_key=pk)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        return tx_hash.hex()

    @classmethod
    def get_link(cls, tx_hash):
        if env.get('TEST'):
            return f'https://rinkeby.etherscan.io/tx/{tx_hash}'
        else:
            return f'https://etherscan.io/tx/{tx_hash}'

    @classmethod
    def is_transaction_delivered(cls, tx_hash):
        return bool(web3.eth.getTransactionReceipt(tx_hash))

    @classmethod
    def get_tx_amount(cls, tx_hash):
        for _ in range(5):
            tx = web3.eth.getTransaction(tx_hash)
            if tx:
                return cls.from_subunit(int(tx['value']))
            time.sleep(3)

        raise Exception('No transaction')
