import re

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import NICKNAME_CHANGE
from bot.translations.translations import sm


@dp.callback_query_handler(lambda msg: re.match(r'^nickname_change$', msg.data))
async def edit_nickname(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    text, k = await dh.nickname_change(message.from_user.id)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.set_state(NICKNAME_CHANGE)


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=NICKNAME_CHANGE)
async def cancel_change_nickname(message: types.Message, state: FSMContext):
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()


@dp.message_handler(lambda msg: re.match(r'^[a-zA-Z0-9]{3,10}$', msg.text), state=NICKNAME_CHANGE)
async def nickname_change(message: types.Message, state):
    text, k = await dh.change_nickname(message.from_user.id, message.text)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state(with_data=True)
