from aiogram import Dispatcher
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.states import WITHDRAW_CHOOSE_ADDRESS, WITHDRAW_CHOOSE_AMOUNT
from .urls.admin import *
from .urls.create_order import *
from .urls.requisites import *
from .urls.begin_deal import *
from .urls.processing_deal import *
from .urls.send_message import *
from .urls.change_nickname import *
from .urls.edit_order import *
from .helpers import rate_limit
from .settings import loop
from .translations.translations import sm


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
    text, k = await dh.accounts(message.from_user.id)
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


@dp.message_handler(lambda msg: msg.text.startswith(sm('settings')))
async def trading(message: types.Message):
    text, k = await dh.settings(message.from_user.id)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('market_choose_symbol'))
async def account(message: types.CallbackQuery):
    await message.answer()
    text, k = await dh.symbol_market(int(message.data.split()[1]))
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'(buy|sell) [0-9]+', msg.data))
async def symbol_market_action(message: types.CallbackQuery):
    await message.answer()
    action, symbol_id = message.data.split()
    text, k = await dh.symbol_market_action(message.from_user.id, int(symbol_id), action)
    await message.message.edit_text(text=text, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^broker_(buy|sell) [0-9]+ [0-9]+$', msg.data))
async def symbol_broker_market(message: types.CallbackQuery):
    await message.answer()
    splited = message.data.split()
    text, k = await dh.symbol_broker_market(
        telegram_id=message.from_user.id,
        action=splited[0].split('_')[1],
        symbol_id=int(splited[1]),
        broker_id=int(splited[2])
    )
    await message.message.edit_text(text=text, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^my_orders [0-9]+$', msg.data))
async def my_orders(message: types.CallbackQuery):
    symbol_id = int(message.data.split()[1])
    text, k = await dh.my_orders(message.from_user.id, symbol_id)
    await message.message.edit_text(text=text, reply_markup=k)


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


@dp.callback_query_handler(lambda msg: re.match(r'^order [0-9a-z]+$', msg.data))
async def get_order(message: types.CallbackQuery):
    await message.answer()
    order_id = message.data.split()[1]
    text, k = await dh.get_order_info(message.message.chat.id, order_id)
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: re.match(r'^/o[0-9a-z]+$', msg.text))
async def get_order_text(message: types.Message):
    order_id = message.text[2:]
    text, k = await dh.get_order_info(message.chat.id, order_id)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: re.match(r'^deal [0-9a-z]+$', msg.data))
async def get_deal(message: types.CallbackQuery):
    await message.answer()
    deal_id = message.data.split()[1]
    text, k = await dh.get_deal(message.from_user.id, deal_id)
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: re.match(r'^/d[0-9a-z]+$', msg.text))
async def get_deal_text(message: types.Message):
    deal_id = message.text[2:]
    text, k = await dh.get_deal(message.from_user.id, deal_id)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: re.match(r'^/tr[0-9a-z]+$', msg.text))
async def get_user(message: types.Message):
    nickname = message.text[3:]
    text, k = await dh.get_user_info(message.from_user.id, nickname)
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
    scheduler.add_job(dh.get_updates, 'interval', seconds=1, max_instances=1)
    scheduler.start()
    executor.start_polling(dp, loop=loop, on_shutdown=shutdown)
