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
async def edit_requisite(message: types.CallbackQuery, state):
    await message.answer()
    broker_id = int(message.data.split()[1])
    text, k = await dh.edit_requisite(broker_id)
    await send_message(text=text, reply_markup=k, chat_id=message.from_user.id)
    await state.set_state(EDIT_REQUISITE)
    await state.set_data({'broker_id': broker_id})


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=EDIT_REQUISITE)
async def cancel_enter_requisites(message: types.Message, state):
    await state.reset_state(with_data=True)
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)


@dp.message_handler(state=EDIT_REQUISITE)
async def requisites_broker(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.update_requisite(message.from_user.id, data['broker_id'], message.text)
    await send_message(text=text, reply_markup=k, chat_id=message.from_user.id)
    await state.reset_state(with_data=True)
