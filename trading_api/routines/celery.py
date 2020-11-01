import os
from celery import Celery
from datetime import timedelta
from celery.task import periodic_task


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_api.settings')

app = Celery('handler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


single_jobs = dict.fromkeys(
    [
        'usdt_dep', 'usdt_width',
        'eth_dep', 'eth_width',
        'btc_dep', 'btc_dep',
        'prizm_dep', 'prizm_width'
    ],
    False
)


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
    from .tasks.crypto.eth.create_deposits import create_deposit_eth
    if single_jobs['eth_dep']:
        return
    single_jobs['eth_dep'] = True
    create_deposit_eth()
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
    from .tasks.crypto.usdt.deposit import deposit_usdt
    if single_jobs['usdt_dep']:
        return
    single_jobs['usdt_dep'] = True
    deposit_usdt()
    single_jobs['usdt_dep'] = False


@periodic_task(run_every=timedelta(minutes=1))
def withdraw_usdt():
    from .tasks.crypto.usdt.withdraw import withdraw_usdt
    if single_jobs['usdt_width']:
        return
    single_jobs['usdt_width'] = True
    withdraw_usdt()
    single_jobs['usdt_width'] = False


@periodic_task(run_every=timedelta(minutes=5))
def create_deposit_prizm():
    from .tasks.crypto.prizm.create_deposit import create_deposit_prizm
    if single_jobs['prizm_dep']:
        return
    single_jobs['prizm_dep'] = True
    create_deposit_prizm()
    single_jobs['prizm_dep'] = False


@periodic_task(run_every=timedelta(seconds=15))
def process_deposit_prizm():
    from .tasks.crypto.prizm.process_deposit import process_deposit_prizm
    process_deposit_prizm()


@periodic_task(run_every=timedelta(minutes=1))
def withdraw_prizm():
    from .tasks.crypto.prizm.withdraw import withdraw_prizm
    if single_jobs['prizm_width']:
        return
    single_jobs['prizm_width'] = True
    withdraw_prizm()
    single_jobs['prizm_width'] = False


@periodic_task(run_every=timedelta(seconds=15))
def deal_process_timeouts():
    from .tasks.deals.timeouts import process_timeouts
    process_timeouts()


@periodic_task(run_every=timedelta(minutes=1))
def send_message():
    from .tasks.notifications.send_notifications import send_process
    send_process()
