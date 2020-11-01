import re

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import EDIT_ORDER_LIMITS, EDIT_ORDER_DETAILS, EDIT_ORDER_RATE, ORDER_DELETE
from bot.translations.translations import get_trans_list, sm
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
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=[EDIT_ORDER_DETAILS, EDIT_ORDER_RATE, EDIT_ORDER_LIMITS])
async def cancel_send_message(message: types.Message, state: FSMContext):
    await state.reset_state()
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()


@dp.message_handler(lambda msg: re.match(r'^-?[0-9]{1,2}%$', msg.text), state=EDIT_ORDER_RATE)
@dp.message_handler(lambda msg: re.match(r'^-?[0-9.,]{1,3}%$', msg.text), state=EDIT_ORDER_RATE)
async def edit_rate_percents(message: types.Message, state):
    coefficient = str(round((float(message.text.replace(',', '.')[:-1]) + 100) / 100, 3))
    data = await state.get_data()
    text, k = await dh.update_order(message.from_user.id, data['order_id'], {'coefficient': coefficient})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: is_string_a_number(msg.text.replace(',', '.')), state=EDIT_ORDER_RATE)
async def edit_rate_fixed(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.update_order(
        message.from_user.id, data['order_id'],
        {'rate': message.text.replace(',', '.'), 'coefficient': None}
    )
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: re.match(r'^[0-9 ]+-[0-9 ]+$', msg.text), state=EDIT_ORDER_LIMITS)
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


@dp.callback_query_handler(lambda msg: re.match(r'^order_edit_activity [0-9a-z]+$', msg.data))
async def edit_order_activity(message: types.CallbackQuery):
    await message.answer()
    order_id = message.data.split()[1]
    text, k = await dh.edit_order_activity(message.from_user.id, order_id)
    await message.message.edit_text(text, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^(on|off)_all_orders$', msg.data))
async def edit_orders_activity(message: types.CallbackQuery):
    await message.answer()
    await message.message.edit_reply_markup()
    action = message.data.split('_')[0]
    text, k = await dh.change_activity_all_orders(message.from_user.id, action)
    await message.message.edit_reply_markup(reply_markup=k)
