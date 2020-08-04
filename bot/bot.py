import re
from typing import Union

from aiogram import types, Dispatcher
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.states import SELECT_BROKER, WITHDRAW_CHOOSE_ADDRESS, WITHDRAW_CHOOSE_AMOUNT, CHOOSE_LIMITS, CHOOSE_RATE
from bot.utils.utils import is_string_a_number
from .translations.translations import sm
from .data_handler import dh, send_message
from .helpers import rate_limit
from .settings import dp, loop


@dp.message_handler(commands=['id'])
@rate_limit(1)
async def get_id(message: types.Message):
    await message.reply(text=message.chat.id)


@dp.message_handler(commands=['start'], state='*')
@rate_limit(1)
async def start(message: types.Message, state):
    await state.reset_state(with_data=True)
    text, k = await dh.start(msg=message)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('accounts')))
async def accounts(message: types.Message):
    text, k = await dh.accounts()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('account'))
async def account(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.account(message.from_user.id, int(message.data.split()[1]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('create_account'))
async def create_account(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.create_account(message.from_user.id, int(message.data.split()[1]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('trading')))
async def trading(message: types.Message):
    text, k = await dh.market()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('market_choose_symbol'))
async def account(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.symbol_market(int(message.data.split()[1]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('buy'))
async def buy(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.symbol_market_buy(int(message.data.split()[1]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('sell'))
async def sell(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.symbol_market_sell(int(message.data.split()[1]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('broker_buy'))
async def broker_buy(message: types.CallbackQuery):
    await message.answer()
    splited = message.data.split()
    text, k = await dh.symbol_broker_market_sell(int(splited[1]), int(splited[2]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^my_orders [0-9]+$', msg.data))
async def my_orders(message: types.CallbackQuery):
    symbol_id = int(message.data.split()[1])
    text, k = await dh.my_orders(message.from_user.id, symbol_id)
    await message.message.edit_text(text=text, reply_markup=k)


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
async def cancel_create_lot(message: Union[types.CallbackQuery, types.Message], state):
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


@dp.message_handler(lambda msg: re.match(r'^[0-9\w]+-[0-9\w]+$', msg.text), state=CHOOSE_LIMITS)
async def done_choose_limits(message: types.Message, state):
    limit_from, limit_to = map(lambda x: int(x.replace(' ', '')), message.text.split('-'))
    data = await state.get_data()
    text, k = await dh.choose_rate()
    await state.set_data({**data, **{'limit_from': limit_from, 'limit_to': limit_to}})
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)
    await state.set_state(CHOOSE_RATE)


@dp.message_handler(lambda msg: re.match(r'^-?[0-9]{1,2}%$', msg.text), state=CHOOSE_RATE)
async def choose_rate_percents(message: types.Message, state):
    coefficient = str(round((int(message.text[:-1]) + 100) / 100, 2))
    data = await state.get_data()
    text, k = await dh.create_order(message.from_user.id, {**data, **{'coefficient': coefficient}})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: is_string_a_number(msg.text), state=CHOOSE_RATE)
async def choose_rate_percents(message: types.Message, state):
    data = await state.get_data()
    text, k = await dh.create_order(message.from_user.id, {**data, **{'rate': message.text}})
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)


@dp.message_handler(lambda msg: msg.text.startswith(sm('about')))
async def about(message: types.Message):
    text, k = await dh.about()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')))
async def cancel(message: types.Message):
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('get_address'))
async def get_address(message: types.CallbackQuery):
    await message.answer()
    text = f'<pre>{message.data.split()[1]}</pre>'
    await send_message(text=text, chat_id=message.message.chat.id)


@dp.callback_query_handler(lambda msg: re.match(r'^order [0-9]+$', msg.data))
async def get_order(message: types.CallbackQuery):
    await message.answer()
    order_id = int(message.data.split()[1])
    text, k = await dh.get_order(message.message.chat.id, order_id)
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: re.match(r'^/tr[0-9a-z]+$', msg.text))
async def get_user(message: types.Message):
    nickname = message.text[3:]
    text, k = await dh.get_user(message.from_user.id, nickname)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('withdraw'))
@rate_limit(5)
async def withdraw(message: types.CallbackQuery, state):
    await message.answer()
    symbol_id = int(message.data.split()[1])
    (text, k), status = await dh.withdraw(message.from_user.id, symbol_id)
    if status:
        await state.set_data({'symbol_id': symbol_id})
        await state.set_state(WITHDRAW_CHOOSE_ADDRESS)
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=WITHDRAW_CHOOSE_ADDRESS)
@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=WITHDRAW_CHOOSE_AMOUNT)
@rate_limit(1)
async def cancel_withdraw(message: types.Message, state):
    await state.reset_state(with_data=True)
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler(state=WITHDRAW_CHOOSE_ADDRESS)
@rate_limit(1)
async def handle_address(message: types.Message, state):
    data = await state.get_data()
    address = message.text.strip()
    (text, k), success = await dh.process_address(message.from_user.id, address, data['symbol_id'])
    if success:
        await state.set_state(WITHDRAW_CHOOSE_AMOUNT)
        await state.set_data({**data, **{'address': address}})
    else:
        await state.reset_state(with_data=True)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler(state=WITHDRAW_CHOOSE_AMOUNT)
@rate_limit(1)
async def handle_amount(message: types.Message, state):
    data = await state.get_data()
    (text, k), success = await dh.process_amount_withdraw(
        telegram_id=message.from_user.id,
        address=data['address'],
        symbol_id=data['symbol_id'],
        amount=message.text
    )
    if success:
        await state.reset_state(with_data=True)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data == 'ref')
async def referral(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.referral(message.from_user.id)
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('about')))
async def about(message: types.Message):
    text, k = await dh.about()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler()
@rate_limit(1)
async def default(message: types.Message):
    pass
    # text, k = await dh.unknown_command()
    # await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler()
@rate_limit(1)
async def default_inline(message: types.CallbackQuery, state):
    await state.reset_state(with_data=True)
    text, k = await dh.unknown_command()
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.errors_handler()
async def some_error(update: types.update.Update, error):
    user_telegram_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    text, k = await dh.some_error()
    await send_message(chat_id=user_telegram_id, text=text, reply_markup=k)
    s = dp.current_state(user=user_telegram_id, chat=user_telegram_id)
    await s.finish()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    scheduler = AsyncIOScheduler(event_loop=loop)
    scheduler.add_job(dh.get_updates, 'interval', seconds=5, max_instances=1)
    scheduler.start()
    executor.start_polling(dp, loop=loop, on_shutdown=shutdown)
