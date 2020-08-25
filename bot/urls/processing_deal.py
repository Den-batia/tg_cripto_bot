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


@dp.callback_query_handler(lambda msg: re.match(r'^deal_send_fiat [0-9a-z]+$', msg.data))
async def deal_send_fiat(message: types.CallbackQuery):
    await message.answer()
    deal_id = message.data.split()[1]
    text, k = await dh.send_fiat(message.from_user.id, deal_id)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^deal_send_crypto [0-9a-z]+$', msg.data))
async def deal_send_crypto(message: types.CallbackQuery):
    await message.answer()
    deal_id = message.data.split()[1]
    text, k = await dh.send_crypto(message.from_user.id, deal_id)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^deal_(like|dislike) [0-9a-z]+$', msg.data))
async def deal_rate_user(message: types.CallbackQuery):
    await message.answer()
    await message.message.edit_reply_markup()
    action, deal_id = message.data.split()
    action = action.split('_')[1]
    text, k = await dh.rate_user(message.from_user.id, deal_id, action)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
