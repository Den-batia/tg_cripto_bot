from datetime import timedelta, timezone, datetime

from api.models import Deal, User, Account
from django.db.transaction import atomic

from api.api import BalanceManagementMixin

from utils.redis_queue import NotificationsQueue

MINUTES_TO_TIMEOUT = 5


def process_timeouts():
    deals_to_timeout = Deal.objects.filter(
        created_at__lt=datetime.now(timezone.utc) - timedelta(minutes=MINUTES_TO_TIMEOUT),
        status=0
    )
    for deal in deals_to_timeout:
        bm = BalanceManagementMixin()
        with atomic():
            bm.unfreeze(deal.mount_crypto_blocked, deal.seller, deal.symbol)
            for user in (deal.buyer, deal.seller):
                NotificationsQueue.put(
                    {
                        'telegram_id': user.telegram_id,
                        'type': 'deal_timeout',
                        'id': deal.id
                    }
                )
            deal.status = -1
            deal.closed_at = datetime.now(timezone.utc)
            deal.save()
