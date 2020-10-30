from datetime import timedelta, timezone, datetime
import time

from api.models import User, Notification
from utils.redis_queue import NotificationsQueue




def send_process():
    notifications = Notification.objects.filter(is_active=True).all()
    if notifications:
        ids = User.objects.values('telegram_id')
        for notification in notifications:
            time_start = datetime.now()
            while ids:
                ids_10 = ids[:10]
                for i in ids_10:
                    NotificationsQueue.put(
                        {
                            'telegram_id': i['telegram_id'],
                            'type': 'send_notifications',
                            'text': notification.text
                        }
                    )
                ids = ids[10:]
                time.sleep(1)
            time_end = datetime.now()
            notification.started_at = time_start
            notification.ended_at = time_end
            notification.is_active = False
            notification.save()