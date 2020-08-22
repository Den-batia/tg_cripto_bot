import os
from celery import Celery
from datetime import timedelta
from celery.task import periodic_task


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_api.settings')

app = Celery('handler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@periodic_task(run_every=timedelta(minutes=1))
def update_rates():
    from .tasks.update_rates import update
    update()


@periodic_task(run_every=timedelta(minutes=2))
def update_order_rates():
    from .tasks.update_order_rates import update
    update()


@periodic_task(run_every=timedelta(minutes=2))
def create_deposits_eth():
    from .tasks.crypto.eth.create_deposits import create
    create()


@periodic_task(run_every=timedelta(seconds=30))
def process_deposits_eth():
    from .tasks.crypto.eth.process_deposits import process
    process()


@periodic_task(run_every=timedelta(seconds=10))
def create_withdraws_eth():
    from .tasks.crypto.eth.withdraw import create
    create()


@periodic_task(run_every=timedelta(seconds=10))
def process_withdraws_eth():
    from .tasks.crypto.eth.confirm_withdraw import confirm
    confirm()


@periodic_task(run_every=timedelta(seconds=15))
def deal_process_timeouts():
    from .tasks.deals.timeouts import process_timeouts
    process_timeouts()
