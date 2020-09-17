from api.models import Symbol, Withdraw, Rates
from crypto.usdt import USDT

from api.api import BalanceManagementMixin
from django.db.transaction import atomic
from utils.redis_queue import NotificationsQueue


def send_tx(withdraw_object: Withdraw):
    gas, gas_price = USDT.get_gas_and_gas_price(
        USDT.to_checksum(withdraw_object.address),
        withdraw_object.amount,
        withdraw_object.user.accounts.filter(symbol__name='usdt').get().private_key
    )
    bm = BalanceManagementMixin()
    with atomic():
        bm.add_frozen(
            -(withdraw_object.amount + withdraw_object.commission_service),
            withdraw_object.user,
            withdraw_object.symbol
        )
        tx_hash = USDT.withdraw(
            target_address=withdraw_object.address,
            amount=withdraw_object.amount,
            gas=gas,
            gas_price=gas_price
        )
        withdraw_object.commission_blockchain = USDT.get_net_commission(gas, gas_price) * Rates.objects.get(symbol__name='usdt').rate
        withdraw_object.tx_hash = tx_hash
        withdraw_object.save()
    NotificationsQueue.put(
        {
            'telegram_id': withdraw_object.user.telegram_id,
            'type': 'withdraw',
            'link': USDT.get_link(tx_hash)
        }
    )
    bm.add_commission(withdraw_object.commission_service - withdraw_object.commission_blockchain,
                      withdraw_object.symbol)


def withdraw():
    symbol = Symbol.objects.get(name='usdt')
    is_withdrawing = Withdraw.objects.filter(tx_hash__isnull=False, confirmed_at__isnull=True, symbol__name__in=('eth', 'usdt')).exists()
    if not is_withdrawing:
        tx_to_send = symbol.withdraws.filter(tx_hash__isnull=True).first()
        if tx_to_send is not None:
            send_tx(tx_to_send)
