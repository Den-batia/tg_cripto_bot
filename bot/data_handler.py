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

    async def check_address_request(self, telegram_id):
        user = await api.get_user(telegram_id)
        if user['balance_requests'] < 1:
            return await rc.deposit(user['balance_requests'], price=0.0001), False
        return await rc.check_address_request(), True

    async def check_address(self, address, telegram_id):
        result = await api.check_address(address, telegram_id)
        return await rc.check_address(**result, address=address)

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
