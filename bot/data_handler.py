import math
from datetime import timedelta, datetime, timezone
from decimal import Decimal

from aiogram.types import Message
from dateutil.parser import parse

from .api import api
from .response_composer import rc
from .settings import bot
from .utils.logger import logger
from .utils.redis_queue import NotificationsQueue
from .utils.utils import get_ref_code, get_ref_link, is_string_a_number, round_down

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
        return await rc.agree_policy()

    async def policy_confirmed(self):
        return await rc.start()

    async def get_updates(self):
        notification = NotificationsQueue.get_nowait()
        while notification is not None:
            meth = getattr(rc, f'get_update_{notification["type"]}')
            text, k = await meth(**notification)
            await send_message(text, chat_id=notification['telegram_id'], reply_markup=k)
            if file_id := notification.get('file_id'):
                await bot.send_document(notification['telegram_id'], file_id)
            if photo_id := notification.get('photo_id'):
                await bot.send_photo(notification['telegram_id'], photo_id)
            notification = NotificationsQueue.get(False)

    async def my_orders(self, telegram_id):
        user = await api.get_user(telegram_id)
        orders = await api.get_user_orders(user['id'])
        return await rc.my_orders(orders)

    async def new_order(self):
        symbols = await api.get_symbols()
        return await rc.new_order(symbols)

    async def new_order_symbol(self, symbol_id):
        return await rc.new_order_symbol(symbol_id)

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

    async def change_activity_all_order(self, telegram_id, action):
        user = await api.get_user(telegram_id)
        orders = await api.get_user_orders(user['id'])
        await api.change_activity_all_order(telegram_id, action)
        return await rc.my_orders(orders)

    async def about(self):
        symbols = await api.get_symbols()
        return await rc.about(symbols)

    async def some_error(self):
        return await rc.unknown_error()

    async def unknown_command(self):
        return await rc.unknown_command()

    async def cancel(self):
        return await rc.cancel()

    async def accounts(self, telegram_id):
        user = await api.get_user(telegram_id)
        symbols = await api.get_symbols()
        accounts = await api.get_accounts(user['id'])
        rates = await api.get_rates()
        total_balance = 0
        for account in accounts['accounts']:
            rate = next(filter(lambda x: x['symbol']['id'] == account['symbol']['id'], rates))['rate']
            total_balance += round(Decimal(account['balance']) * Decimal(rate), 2)
        return await rc.accounts(symbols, accounts['accounts'], total_balance)

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

    async def get_address(self, telegram_id, symbol_id):
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        requisites = [account['address']] if isinstance(account['address'], str) else account['address'].values()
        for requisite in requisites:
            await send_message(f'<pre>{requisite}</pre>', chat_id=telegram_id)

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
        if Decimal(account['balance']) < Decimal(symbol['min_transaction']):
            return await rc.not_enough_money_withdraw(), False
        return await rc.enter_address(symbol['info']), True

    async def process_address(self, telegram_id, address, symbol_id):
        address_check_result = await api.check_address(address, symbol_id)
        if not address_check_result['is_valid']:
            return await rc.address_validation_failed(), None
        symbol = await api.get_symbol(symbol_id)
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        return await rc.enter_amount_withdraw(
            balance=account['balance'],
            min_transaction=symbol['min_transaction'],
            symbol=symbol['name'].upper(),
            commission=symbol['commission']
        ), True

    async def process_amount_withdraw(self, telegram_id, address, symbol_id, amount):
        symbol = await api.get_symbol(symbol_id)
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        if (
                not is_string_a_number(amount) or
                (amount := Decimal(amount)) < Decimal(symbol['min_transaction']) or
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
        is_enough_money = True
        is_requisites_filled = True
        my_account = await self._get_account(user['id'], order['symbol']['id'])
        account_exists = my_account is not None
        if not is_my:
            if order['type'] == 'buy':
                if account_exists:
                    balance = Decimal(my_account['balance'])
                    target_balance = Decimal(order['limit_from']) / Decimal(order['rate'])
                    is_enough_money = balance >= target_balance
                requisite = await self._get_requisite(user['id'], order['broker']['id'])
                is_requisites_filled = bool(requisite) and bool(requisite['requisite'])
        return await rc.order(
            order,
            is_my=is_my,
            is_enough_money=is_enough_money,
            is_requisites_filled=is_requisites_filled,
            account_exists=account_exists
        )

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

    async def balance(self):
        balance = await api.balance()
        return await rc.balance(balance)

    async def users_stat(self):
        users_stat = await api.users_stat()
        return await rc.users_stat(users_stat)

    async def market(self):
        symbols = await api.get_symbols()
        return await rc.market_choose_symbol(symbols)

    async def symbol_market(self, symbol_id):
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market(symbol)

    async def symbol_market_action(self, telegram_id, symbol_id, action):
        user = await api.get_user(telegram_id)
        lots = await api.get_aggregated_orders(symbol_id, sell_buy_reversed[action], user['id'])
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market_action(symbol, lots, action)

    async def symbol_broker_market(self, telegram_id, symbol_id, broker_id, action):
        user = await api.get_user(telegram_id)
        orders = await api.get_orders(symbol_id, broker_id, sell_buy_reversed[action], user['id'])
        symbol = await api.get_symbol(symbol_id)
        broker = await api.get_broker(broker_id)
        return await rc.symbol_broker_market(symbol, broker, orders, action)

    async def requisites(self):
        brokers = await api.get_brokers()
        return await rc.requisites(brokers)

    async def _get_requisite(self, user_id, broker_id):
        try:
            requisite = await api.get_user_requisite(user_id, broker_id=broker_id)
        except:
            requisite = None
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
        old_requisite = await self._get_requisite(user['id'], broker_id)
        if old_requisite is None:
            body = {'requisite': requisite}
        else:
            body = {'requisite': requisite, 'add_info': old_requisite['add_info']}
        await api.patch_user_requisite(user['id'], broker['id'], body)
        text, _ = await self.requisites_broker(telegram_id, broker_id)
        k = await rc.get_main_k()
        return text, k

    async def edit_add_info(self, broker_id):
        broker = await api.get_broker(broker_id)
        return await rc.edit_broker_requisite_add_info(broker)

    async def update_add_info(self, telegram_id, broker_id, add_info):
        user = await api.get_user(telegram_id)
        broker = await api.get_broker(broker_id)
        old_requisite = await self._get_requisite(user['id'], broker_id)
        if old_requisite is not None:
            await api.patch_user_requisite(user['id'], broker['id'], {'add_info': add_info, 'requisite': old_requisite['requisite']})
            text, _ = await self.requisites_broker(telegram_id, broker_id)
            k = await rc.get_main_k()
            return text, k

    async def _validate_begin_deal(self, order, seller_account, seller_id):
        if Decimal(order['limit_from']) / Decimal(order['rate']) > Decimal(seller_account['balance']):
            logger.warning('balance should be more than limit_from')
            raise Exception
        if order['type'] == 'buy':
            balance = Decimal(seller_account['balance'])
            target_balance = Decimal(order['limit_from']) / Decimal(order['rate']) * (1 + Decimal(order['symbol']['deals_commission']))
            is_enough_money = balance >= target_balance
            requisite = await self._get_requisite(seller_id, order['broker']['id'])
            is_requisites_filled = bool(requisite) and bool(requisite['requisite'])
            if not is_requisites_filled or not is_enough_money:
                logger.warning('requisites not filled or not enough money')
                raise Exception

    def _get_seller_id(self, user, order):
        return order['user']['id'] if order['type'] == ORDER_SELL_TYPE else user['id']

    def _get_buyer_id(self, user, order):
        return user['id'] if order['type'] == ORDER_SELL_TYPE else order['user']['id']

    def get_max_amount_deal(self, commission, balance, order):
        balance_limit = math.ceil(balance * Decimal(order['rate']) * (1 - commission)) - 1
        return min(order['limit_to'], balance_limit)

    async def begin_deal(self, telegram_id, order_id):
        user = await api.get_user(telegram_id)
        order = await api.get_order_info(order_id)
        seller_id = self._get_seller_id(user, order)
        account = await self._get_account(seller_id, order['symbol']['id'])
        try:
            await self._validate_begin_deal(order, account, seller_id)
        except Exception as e:
            logger.exception(e)
            return await rc.error_deal_creation(), False
        max_amount = self.get_max_amount_deal(
            commission=Decimal(order['symbol']['deals_commission']),
            balance=Decimal(account['balance']),
            order=order
        )
        return await rc.enter_amount_begin_deal(order['limit_from'], max_amount), True

    async def begin_deal_confirmation(self, telegram_id, order_id, amount):
        new_data = {}
        user = await api.get_user(telegram_id)
        order = await api.get_order_info(order_id)
        seller_id = self._get_seller_id(user, order)
        account = await self._get_account(seller_id, order['symbol']['id'])
        max_amount = self.get_max_amount_deal(
            commission=Decimal(order['symbol']['deals_commission']),
            balance=Decimal(account['balance']),
            order=order
        )
        if amount > max_amount or amount < order['limit_from']:
            text, k = await rc.wrong_amount()
            await send_message(chat_id=telegram_id, text=text, reply_markup=k)
            return await rc.enter_amount_begin_deal(order['limit_from'], max_amount), False, new_data
        if order['type'] == ORDER_BUY_TYPE:
            requisite = await self._get_requisite(user['id'], order['broker']['id'])
        else:
            requisite = None
        if requisite:
            new_data['requisite'] = requisite['requisite']
            new_data['add_info'] = requisite['add_info']
        new_data['amount_crypto'] = str(round_down(amount / Decimal(order['rate'])))
        new_data['amount'] = str(amount)
        new_data['seller_id'] = self._get_seller_id(user, order)
        new_data['buyer_id'] = self._get_buyer_id(user, order)
        new_data['order_id'] = order['id']
        new_data['rate'] = order['rate']
        return await rc.begin_deal_confirmation(order, amount, new_data['amount_crypto'], requisite, sell_buy_reversed), True, new_data

    async def begin_deal_confirmed(self, data):
        order = await api.get_order_info(data['order_id'])
        account = await self._get_account(data['seller_id'], order['symbol']['id'])
        try:
            await self._validate_begin_deal(order, account, data['seller_id'])
        except:
            return await rc.unknown_error()
        deal = await api.create_deal(data)
        return await rc.deal(deal)

    async def get_deal(self, telegram_id, deal_id):
        user = await api.get_user(telegram_id)
        deal = await api.get_deal(deal_id)
        return await rc.deal(deal, user)

    def _validate_user_in_deal(self, user, deal):
        if user['id'] not in (deal['seller']['id'], deal['buyer']['id']):
            raise Exception

    async def confirm_decline_deal(self, telegram_id, deal_id, action):
        deal = await api.get_deal(deal_id)
        user = await api.get_user(telegram_id)
        self._validate_user_in_deal(user, deal)
        if deal['status'] not in [0, 1]:
            return await rc.unknown_error()
        await api.confirm_decline_deal(user['id'], deal['id'], action)
        answers = {
            'confirm': rc.deal_confirmed,
            'decline': rc.deal_declined
        }
        args = []
        if action == 'confirm':
            args.append(deal['order']['type'])
            args.append(deal['seller'])
        return await answers[action](*args)

    async def send_fiat(self, telegram_id, deal_id):
        deal = await api.get_deal(deal_id)
        user = await api.get_user(telegram_id)
        self._validate_user_in_deal(user, deal)
        if deal['status'] != 1:
            return await rc.unknown_error()
        await api.confirm_decline_deal(user['id'], deal['id'], 'send_fiat')
        return await rc.fiat_sent()

    async def open_dispute(self, telegram_id, deal_id):
        deal = await api.get_deal(deal_id)
        user = await api.get_user(telegram_id)
        self._validate_user_in_deal(user, deal)
        if deal['status'] != 2:
            return await rc.unknown_error()
        await api.open_dispute(user['id'], deal['id'])
        return await rc.done()

    async def admin_solve_dispute(self, deal_id, action):
        deal = await api.get_deal(deal_id)
        if deal['status'] != 2:
            return await rc.unknown_error()
        await api.admin_solve_dispute(deal['id'], action)
        return await rc.done()

    async def send_crypto(self, telegram_id, deal_id):
        deal = await api.get_deal(deal_id)
        user = await api.get_user(telegram_id)
        self._validate_user_in_deal(user, deal)
        if deal['status'] != 2:
            return await rc.unknown_error()
        await api.confirm_decline_deal(user['id'], deal['id'], 'send_crypto')
        return await rc.crypto_sent()

    async def rate_user(self, telegram_id, deal_id, action):
        deal = await api.get_deal(deal_id)
        user = await api.get_user(telegram_id)
        target_id = deal['seller']['id'] if user['id'] == deal['buyer']['id'] else deal['buyer']['id']
        action = True if action == 'like' else False
        await api.rate_user(user['id'], target_id, deal['id'], action)
        return await rc.done()

    async def send_message(self):
        return await rc.send_message()

    async def send_message_confirmed(self, telegram_id, user_id, text, file_id=None, photo_id=None):
        user = await api.get_user(telegram_id)
        await api.send_message(sender_id=user['id'], receiver_id=user_id, text=text, file_id=file_id, photo_id=photo_id)
        return await rc.message_sent()

    async def settings(self, telegram_id):
        user = await api.get_user(telegram_id)
        return await rc.settings(user)

    async def nickname_change(self, telegram_id):
        user = await api.get_user(telegram_id)
        if (
                (last_change := user['last_nickname_change']) is not None
                and
                parse(last_change) + timedelta(days=30) > datetime.now(timezone.utc)
        ):
            return await rc.unknown_error()
        return await rc.nickname_change()

    async def change_nickname(self, telegram_id, new_nickname):
        user = await api.get_user(telegram_id)
        try:
            await api.change_nickname(user['id'], new_nickname)
        except:
            return await rc.nickname_change(), False
        return await rc.done(), True


dh = DataHandler()
