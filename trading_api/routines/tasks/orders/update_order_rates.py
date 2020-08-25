import logging

from api.models import Symbol, Order

logger = logging.getLogger('update_order_rates')


def update():
    for symbol in Symbol.objects.all():
        rate = symbol.rates.first()
        orders = []
        for order in symbol.orders.filter(coefficient__isnull=False).all():
            order.rate = order.coefficient * rate.rate
            orders.append(order)
        Order.objects.bulk_update(orders, ['rate'])
