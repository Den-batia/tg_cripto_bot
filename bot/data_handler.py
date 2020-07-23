from aiogram.types import Message

from .api import api
from .response_composer import rc
from .settings import bot
from .utils.logger import logger
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

    async def about(self):
        return await rc.about()

    async def some_error(self):
        return await rc.unknown_error()

    async def cancel(self):
        return await rc.cancel()

    async def accounts(self):
        symbols = await api.get_symbols()
        return await rc.accounts(symbols)

    async def _get_account(self, user_id, symbol_id):
        user_accounts = (await api.get_accounts(user_id))['accounts']
        return next((acc for acc in user_accounts if symbol_id == acc['symbol']['id']), None)

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

    async def referral(self, telegram_id):
        user = await api.get_user(telegram_id)
        text, k = await rc.referral()
        await send_message(text, telegram_id, reply_markup=k)
        return await get_ref_link(user['ref_code']), None


dh = DataHandler()
