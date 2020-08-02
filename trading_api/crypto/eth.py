import time
from web3 import Web3, HTTPProvider
from os import environ as env


if env.get('TEST'):
    web3 = Web3(HTTPProvider('https://rinkeby.infura.io/v3/6ebd1c9c66c445eeb9715eb27eab7f60'))
    chain = 4
else:
    web3 = Web3(HTTPProvider(''))
    chain = 1


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
    def get_balance(cls, pk=None, address=None):
        if pk is not None:
            address = cls.get_address_from_pk(pk)
        elif address is not None:
            if not web3.isAddress(address.lower()):
                raise ValueError('Wrong address')
        else:
            address = cls.get_address_from_pk(cls.PK)

        return cls.from_subunit(web3.eth.getBalance(address))

    @classmethod
    def get_net_commission(cls, net_commission, units=False, is_internal_call=True):
        gas = 21000
        gas_price = web3.toWei(net_commission, 'gwei')
        if is_internal_call:
            return gas, gas_price

        net_commission = gas * gas_price

        if units:
            net_commission = cls.from_subunit(net_commission)
        return net_commission

    @classmethod
    def _create_tx(cls, amount, to, from_address, gwei=60, commission=0):
        gas, gas_price = cls.get_net_commission(gwei)
        amount = cls.to_subunit(amount)
        value_with_commission = amount - gas * gas_price - commission

        transaction = {
            'to': to,
            'value': int(value_with_commission),
            'gas': int(gas),
            'gasPrice': gas_price,
            'nonce': web3.eth.getTransactionCount(from_address),
            'chainId': chain
        }
        return transaction

    @classmethod
    def create_tx_out(cls, address, amount, commission, net_commission):
        account = web3.eth.account.privateKeyToAccount(cls.PK)
        to = web3.toChecksumAddress(address)
        tx = cls._create_tx(
            amount=amount, to=to, from_address=account.address,
            commission=commission, net_commission=net_commission
        )
        signed_txn = web3.eth.account.signTransaction(tx, private_key=cls.PK)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return tx_hash.hex()

    @classmethod
    def create_tx_in(cls, pk, gwei):
        balance = cls.get_balance(pk=pk)
        system_address = web3.eth.account.privateKeyToAccount(cls.PK).address
        from_address = web3.eth.account.privateKeyToAccount(pk).address
        tx = cls._create_tx(
            amount=balance, to=system_address,
            from_address=from_address, gwei=gwei
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
