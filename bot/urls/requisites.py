import re

from aiogram import types

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import EDIT_REQUISITE
from bot.translations.translations import sm


@dp.message_handler(lambda msg: msg.text.startswith(sm('requisites')))
async def requisites(message: types.Message):
    text, k = await dh.requisites()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'requisite_broker [0-9]+', msg.data))
async def requisites_broker(message: types.CallbackQuery):
    broker_id = int(message.data.split()[1])
    text, k = await dh.requisites_broker(message.from_user.id, broker_id)
    await message.message.edit_text(text=text, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'edit_requisite [0-9]+', msg.data))
async def requisites_broker(message: types.CallbackQuery, state):
    broker_id = int(message.data.split()[1])
    text, k = await dh.edit_requisite(broker_id)
    await message.message.edit_text(text=text, reply_markup=k)
    await state.set_state(EDIT_REQUISITE)
    await state.set_data({'broker_id': broker_id})


@dp.message_handler(state=EDIT_REQUISITE)
async def requisites_broker(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.edit_requisite_confirm(message.from_user.id, data['broker_id'])
    await message.edit_text(text=text, reply_markup=k)
    await state.reset_state(with_data=True)
