from datetime import timedelta, timezone, datetime
import time

from api.models import User, Notification
from utils.redis_queue import NotificationsQueue




def send_process():
    notifications = Notification.objects.filter(ended_at=None).all()

    if notifications:
        ids = list(User.objects.values('telegram_id'))
        for notification in notifications:

            time_start = datetime.now(timezone.utc)
            notification.started_at = time_start
            notification.save()

            while len(ids) > 0:
                ids_10 = ids[:1]
                for i in ids_10:
                    NotificationsQueue.put(
                        {
                            'telegram_id': i['telegram_id'],
                            'type': 'send_notifications',
                            'text': notification.text
                        }
                    )
                    ids.pop(0)
                time.sleep(1)
            time_end = datetime.now(timezone.utc)
            notification.ended_at = time_end
            notification.save()