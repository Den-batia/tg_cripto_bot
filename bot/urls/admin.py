import re

from aiogram import types

from bot.data_handler import dh, send_message
from bot.settings import dp


@dp.callback_query_handler(lambda msg: re.match(r'^verify [0-9a-z]+$', msg.data))
async def verify_user(message: types.CallbackQuery):
    await message.answer()
    if not await dh.is_user_admin(message.from_user.id):
        text, k = await dh.unknown_command()
        await send_message(text, chat_id=message.from_user.id, reply_markup=k)
    else:
        user = message.data.split()[1]
        text, k = await dh.verify(message.from_user.id, user)
        await message.message.edit_text(text=text, reply_markup=k)


@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    if not await dh.is_user_admin(message.from_user.id):
        text, k = await dh.unknown_command()
        await send_message(text, chat_id=message.from_user.id, reply_markup=k)
    else:
        text, k = await dh.balance()
        await send_message(text=text, reply_markup=k, chat_id=message.from_user.id)


@dp.message_handler(commands=['ad_users'])
async def users_stat(message: types.Message):
    if not await dh.is_user_admin(message.from_user.id):
        text, k = await dh.unknown_command()
        await send_message(text, chat_id=message.from_user.id, reply_markup=k)
    else:
        text, k = await dh.users_stat()
        await send_message(text=text, reply_markup=k, chat_id=message.from_user.id)


@dp.callback_query_handler(lambda msg: re.match(r'^dispute_admin_(buyer|seller)_win [0-9a-z]+$', msg.data))
async def admin_solve_dispute(message: types.CallbackQuery):
    await message.answer()
    if not await dh.is_user_admin(message.from_user.id):
        text, k = await dh.unknown_command()
        await send_message(text, chat_id=message.from_user.id, reply_markup=k)
    else:
        action, deal_id = message.data.split()
        action = action.split('_')[2]
        await dh.admin_solve_dispute(deal_id, action)
