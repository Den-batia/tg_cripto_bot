from collections import defaultdict
from decimal import Decimal
from api.models import Rates, Symbol, Order

from utils.redis_queue import NotificationsQueue


def update_active_order(order, balance):
    target_balance = Decimal(order.limit_from) / order.rate
    if (
        balance < target_balance
        or
        not (req := order.user.requisites.filter(broker_id=order.broker_id).first())
        or
        not req
    ):
        order.is_system_active = False
        if order.is_active:
            NotificationsQueue.put(
                {
                    'telegram_id': order.user.telegram_id,
                    'type': 'order_deactivated',
                    'id': order.id
                }
            )
    return order


def update_not_active_order(order, balance):
    target_balance = Decimal(order.limit_from) / order.rate
    if (
            balance >= target_balance
            and
            (req := order.user.requisites.filter(broker_id=order.broker_id).first())
            and
            req.requisite
    ):
        order.is_system_active = True
        if order.is_active:
            NotificationsQueue.put(
                {
                    'telegram_id': order.user.telegram_id,
                    'type': 'order_activated',
                    'id': order.id
                }
            )
    return order


def update_orders_activations():
    for symbol in Symbol.objects.all():
        user_balances = {}
        orders = []
        for order in symbol.orders.filter(is_deleted=False, type='sell'):
            balance = user_balances.get(
                order.user_id,
                order.user.accounts.filter(symbol=symbol).first().balance
            )
            user_balances[order.user_id] = balance
            if order.is_system_active:
                orders.append(update_active_order(order, balance))
            else:
                orders.append(update_not_active_order(order, balance))
        Order.objects.bulk_update(orders, ['is_system_active'])

