from datetime import timedelta, timezone, datetime
from decimal import Decimal

from api.models import Deal, User, Account
from django.db.transaction import atomic

from api.api import BalanceManagementMixin

from utils.redis_queue import NotificationsQueue

MINUTES_FOR_DISPUTE = 30


def process_deal(deal, bm: BalanceManagementMixin):
    deal.status = 3
    deal.save()
    bm.add_frozen(-deal.amount_crypto, deal.seller, deal.symbol)
    commission = Decimal('0.001') * deal.amount_crypto
    earning = deal.amount_crypto - commission
    deal.commission = commission
    deal.closed_at = datetime.now(timezone.utc)
    bm.add_balance(earning, deal.seller, deal.symbol)
    for user in (deal.buyer, deal.seller):
        NotificationsQueue.put(
            {
                'telegram_id': user.telegram_id,
                'type': 'deal_dispute_closed',
                'id': deal.id
            }
        )


def cancel_deal(deal, bm: BalanceManagementMixin):
    bm.unfreeze(deal.amount_crypto, deal.seller, deal.symbol)
    for user in (deal.buyer, deal.seller):
        NotificationsQueue.put(
            {
                'telegram_id': user.telegram_id,
                'type': 'deal_dispute_canceled',
                'id': deal.id
            }
        )
    deal.status = -1
    deal.closed_at = datetime.now(timezone.utc)
    deal.save()


def process():
    deals = Deal.objects.filter(
        dispute__created_at__lt=datetime.now(timezone.utc) - timedelta(minutes=MINUTES_FOR_DISPUTE),
        status=2
    )
    for deal in deals:
        bm = BalanceManagementMixin()
        with atomic():
            if deal.dispute.initiator == deal.buyer:
                process_deal(deal, bm)
            else:
                cancel_deal(deal.bm)
