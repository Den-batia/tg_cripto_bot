from datetime import timedelta, timezone, datetime
import time

from api.models import User, Notification
from utils.redis_queue import NotificationsQueue


def send_process():
    notification = Notification.objects.filter(ended_at__isnull=True, started_at__isnull=True).first()

    if notification is not None:
        telegram_ids = User.objects.values('telegram_id')
        notification.started_at = datetime.now(timezone.utc)
        notification.save()

        for item in telegram_ids:
            NotificationsQueue.put(
                {
                    'telegram_id': item['telegram_id'],
                    'type': 'send_notifications',
                    'text': notification.text
                }
            )
            time.sleep(0.1)
        notification.ended_at = datetime.now(timezone.utc)
        notification.save()
