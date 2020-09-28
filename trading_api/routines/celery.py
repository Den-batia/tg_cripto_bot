import os
from celery import Celery
from datetime import timedelta
from celery.task import periodic_task


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_api.settings')

app = Celery('handler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


single_jobs = {
    'usdt_dep': False,
    'eth_dep': False,
    'btc_dep': False,
    'usdt_width': False,
    'eth_width': False,
}


@periodic_task(run_every=timedelta(minutes=1))
def update_rates():
    from .tasks.update_rates import update
    update()


@periodic_task(run_every=timedelta(minutes=2))
def update_order_rates():
    from .tasks.orders.update_order_rates import update
    update()


@periodic_task(run_every=timedelta(seconds=15))
def update_order_activations():
    from .tasks.orders.update_order_activation import update_orders_activations
    update_orders_activations()


@periodic_task(run_every=timedelta(minutes=2))
def create_deposits_eth():
    from .tasks.crypto.eth.create_deposits import create
    if single_jobs['eth_dep']:
        return
    single_jobs['eth_dep'] = True
    create()
    single_jobs['eth_dep'] = False


@periodic_task(run_every=timedelta(seconds=30))
def process_deposits_eth():
    from .tasks.crypto.eth.process_deposits import process
    process()


@periodic_task(run_every=timedelta(seconds=10))
def create_withdraws_eth():
    from .tasks.crypto.eth.withdraw import create
    if single_jobs['eth_width']:
        return
    single_jobs['eth_width'] = True
    create()
    single_jobs['eth_width'] = False


@periodic_task(run_every=timedelta(seconds=10))
def process_withdraws_eth():
    from .tasks.crypto.eth.confirm_withdraw import confirm
    confirm()


@periodic_task(run_every=timedelta(minutes=20 if os.environ.get('TEST') is None else 2))
def withdraw_btc():
    from .tasks.crypto.btc.withdraw import withdraw
    withdraw()


@periodic_task(run_every=timedelta(seconds=15))
def deposit_btc():
    from .tasks.crypto.btc.deposit import process_deposit
    if single_jobs['btc_dep']:
        return
    single_jobs['btc_dep'] = True
    process_deposit()
    single_jobs['btc_dep'] = False


@periodic_task(run_every=timedelta(minutes=1))
def deposit_usdt():
    from .tasks.crypto.usdt.deposit import deposit
    print(single_jobs['usdt_dep'])
    if single_jobs['usdt_dep']:
        return
    single_jobs['usdt_dep'] = True
    deposit()
    single_jobs['usdt_dep'] = False


@periodic_task(run_every=timedelta(minutes=1))
def deposit_usdt():
    from .tasks.crypto.usdt.withdraw import withdraw
    if single_jobs['usdt_width']:
        return
    single_jobs['usdt_width'] = True
    withdraw()
    single_jobs['usdt_width'] = False


@periodic_task(run_every=timedelta(seconds=15))
def deal_process_timeouts():
    from .tasks.deals.timeouts import process_timeouts
    process_timeouts()
