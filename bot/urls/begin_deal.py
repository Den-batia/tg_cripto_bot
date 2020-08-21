import re
from decimal import Decimal

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import BEGIN_DEAL_ENTER_AMOUNT, CONFIRM_BEGIN_DEAL
from bot.translations.translations import sm, get_trans_list
from bot.utils.utils import is_string_a_number


@dp.callback_query_handler(lambda msg: re.match(r'^begin_deal [0-9a-z]+$', msg.data))
async def edit_order(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    order_id = message.data.split()[1]
    (text, k), status = await dh.begin_deal(message.from_user.id, order_id)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    if status:
        await state.set_state(BEGIN_DEAL_ENTER_AMOUNT)
        await state.set_data({'order_id': order_id})


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=[BEGIN_DEAL_ENTER_AMOUNT, CONFIRM_BEGIN_DEAL])
@dp.message_handler(lambda msg: msg.text in get_trans_list('no'), state=CONFIRM_BEGIN_DEAL)
async def cancel_begin_deal(message: types.Message, state: FSMContext):
    await state.reset_state()
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)


@dp.message_handler(lambda msg: is_string_a_number(msg.text), state=BEGIN_DEAL_ENTER_AMOUNT)
async def begin_deal_enter_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = Decimal(message.text)
    text, k = await dh.begin_deal_confirmation(message.from_user.id, data['order_id'], amount)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()

