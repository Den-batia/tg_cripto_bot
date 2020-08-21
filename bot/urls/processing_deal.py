import re

from aiogram import types

from bot.data_handler import dh, send_message
from bot.settings import dp


@dp.callback_query_handler(lambda msg: re.match(r'^(confirm|decline)_deal [0-9a-z]+$', msg.data))
async def confirm_decline_deal(message: types.CallbackQuery):
    await message.answer()
    action, deal_id = message.data.split()
    action = action.split('_')[0]
    text, k = await dh.confirm_decline_deal(message.from_user.id, deal_id, action)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
