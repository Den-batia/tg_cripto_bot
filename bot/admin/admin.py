import re

from aiogram import types

from bot.data_handler import dh, send_message
from bot.settings import dp


def validate_admin(method):
    async def wrapper(*args, **kw):
        if dh.is_user_admin(args[0].from_user.id):
            return await method(*args, **kw)
    return wrapper


@dp.callback_query_handler(lambda msg: re.match(r'^verify [0-9a-z]+$', msg.data))
async def verify_user(message: types.CallbackQuery):
    await message.answer()
    user = message.data.split()[1]
    text, k = await dh.verify(message.from_user.id, user)
    await message.message.edit_text(text=text, reply_markup=k)
