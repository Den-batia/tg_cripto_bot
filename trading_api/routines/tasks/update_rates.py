import logging

import requests

from api.models import Rates, Symbol

logger = logging.getLogger('update_rates')


def get_rates():
    rates = requests.get(
        'https://api.coingecko.com/api/v3/simple/price?ids=ethereum,tether,prizm&vs_currencies=rub'
    ).json()
    rates['eth'] = rates.pop('ethereum')
    rates['usdt'] = rates.pop('tether')
    logger.debug(f'UPDATE RATE, new rate = {rates}')
    return rates


def update():
    for symbol_name, currencies in get_rates().items():
        symbol = Symbol.objects.get(name=symbol_name)
        for currency, new_rate in currencies.items():
            Rates.objects.update_or_create(symbol=symbol, defaults={'rate': new_rate})
