import re
from typing import Union

from aiogram import types

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import CHOOSE_RATE, CHOOSE_LIMITS, SELECT_BROKER
from bot.translations.translations import sm
from bot.utils.utils import is_string_a_number


@dp.callback_query_handler(lambda msg: re.match(r'^new_order [0-9]+$', msg.data))
async def new_order(message: types.CallbackQuery):
    symbol_id = int(message.data.split()[1])
    text, k = await dh.new_order(symbol_id)
    await message.message.edit_text(text=text, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^new_order_brokers [0-9]+ (buy|sell)$', msg.data))
async def new_order_brokers(message: types.CallbackQuery, state):
    await message.answer()
    symbol_id, order_type = message.data.split()[1:]
    text, k = await dh.new_order_brokers()
    await message.message.edit_text(text=text, reply_markup=k)
    await state.set_state(SELECT_BROKER)
    await state.set_data({'symbol': int(symbol_id), 'type': order_type, 'brokers': []})


@dp.callback_query_handler(lambda msg: re.match(r'^(add|remove) broker [0-9]+$', msg.data), state=SELECT_BROKER)
async def update_brokers_list(message: types.CallbackQuery, state):
    await message.answer()
    data = await state.get_data()
    splited_data = message.data.split()
    new_brokers_list, k = await dh.update_brokers_list(data['brokers'], int(splited_data[2]), splited_data[0])
    await state.set_data({**data, **{'brokers': new_brokers_list}})
    await message.message.edit_reply_markup(reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^cancel$', msg.data), state=SELECT_BROKER)
@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=[CHOOSE_LIMITS, CHOOSE_RATE])
async def cancel_create_order(message: Union[types.CallbackQuery, types.Message], state):
    await state.reset_state(with_data=True)
    text, k = await dh.cancel()
    chat_id = message.message.chat.id if isinstance(message, types.CallbackQuery) else message.chat.id
    await send_message(text=text, chat_id=chat_id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^done$', msg.data), state=SELECT_BROKER)
async def done_choose_brokers(message: types.CallbackQuery, state):
    await message.answer()
    await state.set_state(CHOOSE_LIMITS)
    text, k = await dh.choose_limits()
    await message.message.delete()
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: re.match(r'^[0-9 ]+-[0-9 ]+$', msg.text), state=CHOOSE_LIMITS)
async def done_choose_limits(message: types.Message, state):
    limit_from, limit_to = map(lambda x: int(x.replace(' ', '')), message.text.split('-'))
    data = await state.get_data()
    text, k = await dh.choose_rate()
    await state.set_data({**data, **{'limit_from': limit_from, 'limit_to': limit_to}})
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.set_state(CHOOSE_RATE)


@dp.message_handler(lambda msg: is_string_a_number(msg.text), state=CHOOSE_LIMITS)
async def done_choose_limits_only_to(message: types.Message, state):
    limit_from, limit_to = 1, int(float(message.text))
    data = await state.get_data()
    text, k = await dh.choose_rate()
    await state.set_data({**data, **{'limit_from': limit_from, 'limit_to': limit_to}})
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.set_state(CHOOSE_RATE)


# noinspection RegExpRedundantEscape
@dp.message_handler(lambda msg: re.match(r'^-?[0-9]{1,2}%$', msg.text), state=CHOOSE_RATE)
@dp.message_handler(lambda msg: re.match(r'^-?[0-9\.]{1,3}%$', msg.text), state=CHOOSE_RATE)
async def choose_rate_percents(message: types.Message, state):
    coefficient = str(round((int(message.text[:-1]) + 100) / 100, 3))
    data = await state.get_data()
    text, k = await dh.create_order(message.from_user.id, {**data, **{'coefficient': coefficient}})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: is_string_a_number(msg.text), state=CHOOSE_RATE)
async def choose_rate_fixed(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.create_order(message.from_user.id, {**data, **{'rate': message.text}})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)
