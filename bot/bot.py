from aiogram import types, Dispatcher
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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


@dp.message_handler(lambda msg: msg.text.startswith(sm('about')))
async def about(message: types.Message):
    text, k = await dh.about()
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')))
async def cancel(message: types.Message):
    text, k = await dh.cancel(message.text, message.from_user.id)
    await send_message(text=text, chat_id=message.chat.id, reply_markup=k)


@dp.callback_query_handler(lambda msg: msg.data.startswith('get_address'))
async def get_address(message: types.CallbackQuery):
    await message.answer()
    text = f'<pre>{message.data.split()[1]}</pre>'
    await send_message(text=text, chat_id=message.message.chat.id)


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
