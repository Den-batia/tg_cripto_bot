from decimal import Decimal

from ethtoken.abi import EIP20_ABI

from .eth import web3, ETH, chain

CONTRACT_ADDRESS = web3.toChecksumAddress('0xdac17f958d2ee523a2206206994597c13d831ec7')


class USDT(ETH):
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=EIP20_ABI)

    @classmethod
    def from_subunit(cls, val):
        sign = 1
        if val < 0:
            val = abs(val)
            sign = -1
        return sign * web3.fromWei(val, 'picoether')

    @classmethod
    def to_subunit(cls, val):
        sign = 1
        if val < 0:
            val = abs(val)
            sign = -1
        return sign * web3.toWei(val, 'picoether')

    @classmethod
    def get_gas_and_gas_price(cls, to, val, pk):
        gas = cls.contract.functions.transfer(
            to, cls.to_subunit(val)
        ).estimateGas(
            {'from': cls.get_address_from_pk(pk)}
        )
        gas_price = cls.get_gas_price()
        return gas, gas_price

    @classmethod
    def get_target_eth_amount(cls, gas, gas_price):
        return gas * web3.fromWei(gas_price, 'gwei')

    @classmethod
    def get_balance(cls, pk=None):
        if pk is not None:
            address = cls.get_address_from_pk(pk)
        else:
            address = cls.get_address_from_pk(cls.PK)
        balance = cls.contract.functions.balanceOf(address).call()
        return cls.from_subunit(balance)

    @classmethod
    def deposit(cls, pk):
        target_address = cls.get_address_from_pk(cls.PK)
        amount = cls.get_balance(pk)
        gas, gas_price = cls.get_gas_and_gas_price(target_address, amount, pk)
        txn = cls.contract.functions.transfer(
            target_address,
            cls.to_subunit(amount)
        ).buildTransaction({
            'chainId': chain,
            'gas': gas,
            'gasPrice': web3.toWei(gas_price, 'gwei'),
            'nonce': web3.eth.getTransactionCount(cls.get_address_from_pk(pk)),
        })
        signed = web3.eth.account.signTransaction(txn, private_key=pk)
        return web3.eth.sendRawTransaction(signed.rawTransaction).hex()

    @classmethod
    def withdraw(cls, target_address, amount, gas, gwei):
        txn = cls.contract.functions.transfer(
            target_address,
            amount
        ).buildTransaction({
            'chainId': chain,
            'gas': gas,
            'gasPrice': web3.toWei(gwei, 'gwei'),
            'nonce': web3.eth.getTransactionCount(cls.get_address_from_pk(cls.PK))
        })
        signed = web3.eth.account.signTransaction(txn, private_key=cls.PK)
        return web3.eth.sendRawTransaction(signed.rawTransaction).hex()

    # noinspection PyMethodOverriding
    @classmethod
    def get_net_commission(cls, gas, gas_price):
        gas_price = web3.toWei(gas_price, 'gwei')
        return web3.fromWei(gas * gas_price, 'ether')

    @classmethod
    def to_checksum(cls, address):
        return web3.toChecksumAddress(address)

