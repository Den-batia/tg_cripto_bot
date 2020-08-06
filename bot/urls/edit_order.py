import re

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import EDIT_ORDER_LIMITS, EDIT_ORDER_DETAILS, EDIT_ORDER_RATE, ORDER_DELETE
from bot.translations.translations import get_trans_list
from bot.utils.utils import is_string_a_number

states = {
    'limits': EDIT_ORDER_LIMITS,
    'rate': EDIT_ORDER_RATE,
    'details': EDIT_ORDER_DETAILS,
    'delete': ORDER_DELETE
}


@dp.callback_query_handler(lambda msg: re.match(r'^order_edit_(limits|rate|details|delete) [0-9a-z]+$', msg.data))
async def edit_order(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    msg, order = message.data.split()
    edit_type = msg.split('_')[2]
    await state.set_state(states[edit_type])
    await state.set_data({'order_id': order})
    text, k = await dh.edit_order_request(edit_type)
    await message.message.edit_text(text=text, reply_markup=k)


@dp.message_handler(lambda msg: re.match(r'^-?[0-9]{1,2}%$', msg.text), state=EDIT_ORDER_RATE)
async def edit_rate_percents(message: types.Message, state):
    coefficient = str(round((int(message.text[:-1]) + 100) / 100, 2))
    data = await state.get_data()
    text, k = await dh.update_order(message.from_user.id, data['order_id'], {'coefficient': coefficient})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: is_string_a_number(msg.text), state=EDIT_ORDER_RATE)
async def edit_rate_fixed(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.update_order(message.from_user.id, data['order_id'], {'rate': message.text})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: re.match(r'^[0-9\w]+-[0-9\w]+$', msg.text), state=EDIT_ORDER_LIMITS)
async def edit_limits(message: types.Message, state):
    limit_from, limit_to = map(lambda x: int(x.replace(' ', '')), message.text.split('-'))
    data = await state.get_data()
    text, k = await dh.update_order(message.from_user.id, data['order_id'], {'limit_from': limit_from, 'limit_to': limit_to})
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: 0 < len(msg.text) < 1024 , state=EDIT_ORDER_DETAILS)
async def edit_details(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.update_order(message.from_user.id, data['order_id'], {'details': message.text})
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: msg.text in get_trans_list('yes'), state=ORDER_DELETE)
async def delete_order(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.update_order(message.from_user.id, data['order_id'], {'is_deleted': True})
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: msg.text in get_trans_list('no'), state=ORDER_DELETE)
async def delete_order(message: types.Message, state):
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.reset_state(with_data=True)
