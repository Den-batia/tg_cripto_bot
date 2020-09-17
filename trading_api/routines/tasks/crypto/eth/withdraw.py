import logging

from api.models import Symbol, Withdraw
from django.db.transaction import atomic

from crypto.eth import ETH

from utils.redis_queue import NotificationsQueue
from api.api import BalanceManagementMixin


logger = logging.getLogger('eth_withdraw')


def send_tx(withdraw_object: Withdraw):
    gwei = ETH.get_gas_price()
    bm = BalanceManagementMixin()
    with atomic():
        bm.add_frozen(
            -(withdraw_object.amount + withdraw_object.commission_service),
            withdraw_object.user,
            withdraw_object.symbol
        )
        tx_hash = ETH.create_tx_out(address=withdraw_object.address, amount=withdraw_object.amount, gwei=gwei)
        withdraw_object.commission_blockchain = ETH.get_net_commission(gwei)
        withdraw_object.tx_hash = tx_hash
        withdraw_object.save()
    NotificationsQueue.put(
        {
            'telegram_id': withdraw_object.user.telegram_id,
            'type': 'withdraw',
            'link': ETH.get_link(tx_hash)
        }
    )
    bm.add_commission(withdraw_object.commission_service - withdraw_object.commission_blockchain, withdraw_object.symbol)


def create():
    symbol = Symbol.objects.get(name='eth')
    is_withdrawing = Withdraw.objects.filter(tx_hash__isnull=False, confirmed_at__isnull=True, symbol__name__in=('eth', 'usdt')).exists()
    if not is_withdrawing:
        tx_to_send = symbol.withdraws.filter(tx_hash__isnull=True).first()
        if tx_to_send is not None:
            send_tx(tx_to_send)
