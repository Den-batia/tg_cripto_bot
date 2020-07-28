from aiogram.types import Message

from .api import api
from .response_composer import rc
from .settings import bot
from .utils.logger import logger
from .utils.redis_queue import NotificationsQueue
from .utils.utils import get_ref_code, get_ref_link


async def send_message(text, chat_id, reply_markup=None, silent=True):
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception as e:
        if not silent:
            logger.exception(e)
            raise


class DataHandler:
    async def start(self, msg: Message):
        try:
            await api.get_user(msg.from_user.id)
        except:
            ref_code = get_ref_code(msg)
            await api.register_user(msg.from_user.id, ref_code)
        return await rc.start()

    async def get_updates(self):
        notification = NotificationsQueue.get()
        meth = getattr(rc, f'get_update_{notification["type"]}')
        text = await meth(**notification)
        await send_message(text, chat_id=notification['telegram_id'])

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
            return await rc.account(account)

    async def create_account(self, telegram_id, symbol_id):
        user = await api.get_user(telegram_id)
        account = await self._get_account(user['id'], symbol_id)
        if account is None:
            await api.create_account(user['id'], symbol_id)
            account = await self._get_account(user['id'], symbol_id)
        return await rc.account(account)

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

    async def market(self):
        symbols = await api.get_symbols()
        return await rc.market_choose_symbol(symbols)

    async def symbol_market(self, symbol_id):
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market(symbol)

    async def symbol_market_buy(self, symbol_id):
        lots = await api.get_aggregated_orders(symbol_id, 'sell')
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market_buy(symbol, lots)

    async def symbol_market_sell(self, symbol_id):
        lots = await api.get_aggregated_orders(symbol_id, 'buy')
        symbol = await api.get_symbol(symbol_id)
        return await rc.symbol_market_sell(symbol, lots)

    async def symbol_broker_market_sell(self, symbol_id, broker_id):
        orders = await api.get_orders(symbol_id, broker_id, 'buy')
        symbol = await api.get_symbol(symbol_id)
        broker = await api.get_broker(broker_id)
        print(orders)
        return await rc.symbol_broker_market_sell(symbol, broker, orders)


dh = DataHandler()
