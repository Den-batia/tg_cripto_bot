import math
from decimal import Decimal

from aiogram.types import Message

from .api import api
from .response_composer import rc
from .settings import bot
from .utils.logger import logger
from .utils.redis_queue import NotificationsQueue
from .utils.utils import get_ref_code, get_ref_link, is_string_a_number

sell_buy_reversed = {'sell': 'buy', 'buy': 'sell'}
ORDER_SELL_TYPE = 'sell'
ORDER_BUY_TYPE = 'buy'


async def send_message(text, chat_id, reply_markup=None, silent=True):
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        if not silent:
            logger.exception(e)
            raise


# noinspection PyBroadException
class DataHandler:
    async def start(self, msg: Message):
        try:
            await api.get_user(msg.from_user.id)
        except:
            ref_code = get_ref_code(msg)
            await api.register_user(msg.from_user.id, ref_code)
        return await rc.start()

    async def get_updates(self):
        notification = NotificationsQueue.get(False)
        while notification is not None:
            print(notification)
            meth = getattr(rc, f'get_update_{notification["type"]}')
            text, k = await meth(**notification)
            await send_message(text, chat_id=notification['telegram_id'], reply_markup=k)
            notification = NotificationsQueue.get(False)

    async def my_orders(self, telegram_id, symbol_id):
        user = await api.get_user(telegram_id)
        orders = await api.get_user_orders(user['id'], symbol_id)
        return await rc.my_orders(orders, symbol_id)

    async def new_order(self, symbol_id):
        return await rc.new_order(symbol_id)

    async def new_order_brokers(self):
        brokers = await api.get_brokers()
        return await rc.new_order_brokers(brokers)

    async def update_brokers_list(self, current_list, broker_id, action):
        current_list = set(current_list)
        if action == 'add':
            current_list.add(broker_id)
        elif action == 'remove' and broker_id in current_list:
            current_list.remove(broker_id)
        brokers = await api.get_brokers()
        kb = await rc.get_new_order_brokers_kb(brokers, current_list)
        return list(current_list), kb

    async def choose_limits(self):
        return await rc.choose_limits()

    async def choose_rate(self):
        return await rc.choose_rate()

    async def create_order(self, telegram_id, data):
        user = await api.get_user(telegram_id)
        await api.create_order({**data, **{'user_id': user['id']}})
        return await rc.done()

    async def edit_order_request(self, edit_type):
        methods = {
            'limits': rc.choose_limits,
            'rate': rc.choose_rate,
            'details': rc.choose_details,
            'delete': rc.delete_order_confirmation
        }
        return await methods[edit_type]()

    async def update_order(self, telegram_id, order_id, data):
        user = await api.get_user(telegram_id)
        text, k = await rc.done()
        if data.get('is_deleted'):
            await api.delete_order(user['id'], order_id)
            return text, k
        await api.update_order(user['id'], order_id, data)
        await send_message(chat_id=telegram_id, text=text, reply_markup=k)
        return await self.get_order_info(telegram_id, order_id)

    async def edit_order_activity(self, telegram_id, order_id):
        order = await api.get_order_info(order_id)
        user = await api.get_user(telegram_id)
        await api.update_order(user_id=user['id'], order_id=order_id, data={'is_active': not order['is_active']})
        return await self.get_order_info(telegram_id, order_id)

    async def about(self):
        return await rc.about()

    async def some_error(self):
        return await rc.unknown_error()

    async def unknown_command(self):
        return await rc.unknown_command()

    async def cancel(self):
        return await rc.cancel()

    async def accounts(self):
        symbols = await api.get_symbols()
        return await rc.accounts(symbols)

    async def _get_account(self, user_id, symbol_id):
        user_accounts = (await api.get_accounts(user_id))['accounts']
        account = next((acc for acc in user_accounts if acc['symbol']['id'] == symbol_id), None)
        return account

    async def account(self, telegram_id, symbol_id):
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        if account is None:
            return await rc.account_not_exists(symbol_id)
        else:
            return await rc.account(account, user)

    async def create_account(self, telegram_id, symbol_id):
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        if account is None:
            await api.create_account(user['id'], symbol_id)
            account = await self._get_account(user['id'], symbol_id)
        return await rc.account(account, user)

    async def referral(self, telegram_id):
        user = await api.get_user(telegram_id)
        text, k = await rc.referral()
        await send_message(text, telegram_id, reply_markup=k)
        return await get_ref_link(user['ref_code']), None

    async def deposit(self, telegram_id):
        user = await api.get_user(telegram_id)
        text, k = await rc.deposit(balance_requests=user['balance_requests'], price=0.0001)
        await send_message(text, telegram_id, reply_markup=k)
        return f'<pre>{user["address"]}</pre>', None

    async def withdraw(self, telegram_id, symbol_id):
        symbol = await api.get_symbol(symbol_id)
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        if Decimal(account['balance']) < Decimal(symbol['min_withdraw']):
            return await rc.not_enough_money_withdraw(), False
        return await rc.enter_address(), True

    async def process_address(self, telegram_id, address, symbol_id):
        address_check_result = await api.check_address(address, symbol_id)
        if not address_check_result['is_valid']:
            return await rc.address_validation_failed(), None
        symbol = await api.get_symbol(symbol_id)
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        return await rc.enter_amount_withdraw(
            balance=account['balance'],
            min_withdraw=symbol['min_withdraw'],
            symbol=symbol['name'].upper()
        ), True

    async def process_amount_withdraw(self, telegram_id, address, symbol_id, amount):
        symbol = await api.get_symbol(symbol_id)
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        if (
                not is_string_a_number(amount) or
                (amount := Decimal(amount)) < Decimal(symbol['min_withdraw']) or
                amount > Decimal(account['balance'])
        ):
            return await rc.wrong_amount(), False
        await api.create_withdraw(user['id'], symbol_id, amount, address)
        return await rc.transaction_queued(), True

    async def get_order_info(self, telegram_id, order_id):
        user = await api.get_user(telegram_id)
        try:
            order = await api.get_order_info(order_id)
        except:
            return await rc.unknown_command()
        is_my = user['id'] == order['user']['id']
        return await rc.order(order, is_my=is_my)

    async def get_user_info(self, telegram_id, nickname):
        user = await api.get_user(telegram_id)
        target_user = await api.get_user_info(nickname)
        return await rc.user(target_user, is_admin=user['is_admin'])

    async def is_user_admin(self, telegram_id):
        user = await api.get_user(telegram_id)
        return user['is_admin']

    async def verify(self, telegram_id, target_user):
        user = await api.get_user_info(target_user)
        await api.update_user(user['nickname'], dict(is_verify=not user['is_verify']))
        return await self.get_user_info(telegram_id, target_user)

    async def market(self):
        symbols = await api.get_symbols()
        return await rc.market_choose_symbol(symbols)

    async def symbol_market(self, symbol_id):
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market(symbol)

    async def symbol_market_action(self, symbol_id, action):
        lots = await api.get_aggregated_orders(symbol_id, sell_buy_reversed[action])
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market_action(symbol, lots, action)

    async def symbol_broker_market(self, symbol_id, broker_id, action):
        orders = await api.get_orders(symbol_id, broker_id, sell_buy_reversed[action])
        symbol = await api.get_symbol(symbol_id)
        broker = await api.get_broker(broker_id)
        return await rc.symbol_broker_market(symbol, broker, orders, action)

    async def requisites(self):
        brokers = await api.get_brokers()
        return await rc.requisites(brokers)

    async def _get_requisite(self, user_id, broker_id):
        try:
            requisite = (await api.get_user_requisite(user_id, broker_id=broker_id))['requisite']
        except:
            requisite = ''
        return requisite

    async def requisites_broker(self, telegram_id, broker_id):
        user = await api.get_user(telegram_id)
        broker = await api.get_broker(broker_id)
        requisite = await self._get_requisite(user['id'], broker['id'])
        return await rc.broker_requisite(requisite, broker)

    async def edit_requisite(self, broker_id):
        broker = await api.get_broker(broker_id)
        return await rc.edit_broker_requisite(broker)

    async def update_requisite(self, telegram_id, broker_id, requisite):
        user = await api.get_user(telegram_id)
        broker = await api.get_broker(broker_id)
        await api.patch_user_requisite(user['id'], broker['id'], requisite)
        text, _ = await self.requisites_broker(telegram_id, broker_id)
        k = await rc.get_main_k()
        return text, k

    def _validate_begin_deal(self, order, seller_account):
        if Decimal(order['limit_from']) / Decimal(order['rate']) > Decimal(seller_account['balance']):
            raise Exception

    def _get_seller_id(self, user, order):
        return order['user']['id'] if order['type'] == ORDER_SELL_TYPE else user['id']

    async def begin_deal(self, telegram_id, order_id):
        user = await api.get_user(telegram_id)
        order = await api.get_order_info(order_id)
        seller_id = self._get_seller_id(user, order)
        account = await self._get_account(seller_id, order['symbol']['id'])
        try:
            self._validate_begin_deal(order, account)
        except:
            return await rc.unknown_error(), False
        max_amount = min(order['limit_to'], math.ceil(Decimal(account['balance']) * Decimal(order['rate'])))
        return await rc.enter_amount_begin_deal(order['limit_from'], max_amount), True

    async def begin_deal_confirmation(self, telegram_id, order_id, amount):
        user = await api.get_user(telegram_id)
        order = await api.get_order_info(order_id)
        seller_id = self._get_seller_id(user, order)
        account = await self._get_account(seller_id, order['symbol']['id'])
        max_amount = min(order['limit_to'], math.ceil(Decimal(account['balance']) * Decimal(order['rate'])))
        if amount > max_amount or amount < order['limit_from']:
            text, k = await rc.wrong_amount()
            await send_message(chat_id=telegram_id, text=text, reply_markup=k)
            return await rc.enter_amount_begin_deal(order['limit_from'], max_amount), False
        if order['type'] == ORDER_BUY_TYPE:
            requisite = await self._get_requisite(user['id'], order['broker']['id'])
        else:
            requisite = None
        return await rc.begin_deal_confirmation(order, amount, requisite), True

    async def begin_deal_confirmed(self, telegram_id, order_id, amount, amount_crypto, rate):
        user = await api.get_user(telegram_id)
        order = await api.get_order_info(order_id)
        seller_id = self._get_seller_id(user, order)
        account = await self._get_account(seller_id, order['symbol']['id'])
        max_amount = min(order['limit_to'], math.ceil(Decimal(account['balance']) * Decimal(order['rate'])))
        if amount > max_amount or amount < order['limit_from']:
            text, k = await rc.wrong_amount()
            await send_message(chat_id=telegram_id, text=text, reply_markup=k)
            return await rc.enter_amount_begin_deal(order['limit_from'], max_amount), False
        if order['type'] == ORDER_BUY_TYPE:
            requisite = await self._get_requisite(user['id'], order['broker']['id'])
        else:
            requisite = None
        return await rc.begin_deal_confirmation(order, amount, requisite), True


dh = DataHandler()
