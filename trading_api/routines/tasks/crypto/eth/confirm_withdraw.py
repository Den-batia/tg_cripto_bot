import logging
from datetime import timezone, datetime

from api.models import Symbol, Withdraw

from crypto.eth import ETH


logger = logging.getLogger('confirm_eth_withdraw')


def confirm():
    withdrawing_tx: Withdraw = Withdraw.objects.filter(
        tx_hash__isnull=False,
        confirmed_at__isnull=True,
        symbol__name__in=('eth', 'usdt')
    ).first()
    if withdrawing_tx is not None and ETH.is_transaction_delivered(withdrawing_tx.tx_hash):
        withdrawing_tx.confirmed_at = datetime.now(timezone.utc)
        withdrawing_tx.save()
