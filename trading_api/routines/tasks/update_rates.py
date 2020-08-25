import logging

import requests

from api.models import Rates, Symbol

logger = logging.getLogger('update_rates')


def get_rates():
    rates = requests.get(
        'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=rub'
    ).json()
    rates['eth'] = rates.pop('ethereum')
    logger.debug(f'UPDATE RATE, new rate = {rates}')
    return rates


def update():
    for symbol, currencies in get_rates().items():
        symbol = Symbol.objects.get()
        for currency, new_rate in currencies.items():
            rate, created = Rates.objects.get_or_create(symbol=symbol, defaults={'rate': new_rate})
            if not created:
                rate.rate = new_rate
                rate.save()
