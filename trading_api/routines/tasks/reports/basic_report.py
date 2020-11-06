import logging

from api.models import Symbol, Order
from api.api import BalanceView, UsersStatView, DealsStatView
from utils.redis_queue import NotificationsQueue


logger = logging.getLogger('update_order_rates')

REPORT_TELEGRAM_ID = -477008938


def send_report():
    balance = BalanceView.get_balance_data()
    users_stat = UsersStatView.get_users_stat()
    deals_stat = DealsStatView.get_deals_stat()
    text = "<b>Баланс:</b>\n"
    for item in balance:
        text += f"{item['symbol']}:\nБлокчейн: {item['wallet']} {item['symbol']}\nБаза данных: {item['db']} {item['symbol']}\nБаланс: {item['balance']} {item['symbol']}\n\n"

    text += '\n<b>Пользователи:</b>\n'
    for key, value in users_stat.items():
        text += f'{key}: {value}\n'

    text += '\n<b>Сделки:</b>\n'
    for key, value in deals_stat.items():
        text += f'{key}: {value}\n'

    NotificationsQueue.put(
        {
            'telegram_id': REPORT_TELEGRAM_ID,
            'type': 'send_notifications',
            'text': text
        }
    )
