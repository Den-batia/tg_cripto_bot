import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from bot.data_handler import dh, send_message
from bot.settings import dp
from bot.states import SEND_MESSAGE
from bot.translations.translations import sm


@dp.callback_query_handler(lambda msg: re.match(r'^send_message [0-9a-z-]+$', msg.data))
async def send_new_message(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    user_id = message.data.split()[1]
    text, k = await dh.send_message()
    await send_message(text=text, chat_id=message.message.chat.id, reply_markup=k)
    await state.set_data({'user_id': user_id})
    await state.set_state(SEND_MESSAGE)


@dp.message_handler(lambda msg: msg.text.startswith(sm('cancel')), state=SEND_MESSAGE)
async def cancel_send_message(message: types.Message, state: FSMContext):
    await state.reset_state()
    text, k = await dh.cancel()
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()


@dp.message_handler(content_types=[ContentType.DOCUMENT], state=SEND_MESSAGE)
async def send_message_confirmed_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text, k = await dh.send_message_confirmed(
        message.from_user.id,
        data['user_id'],
        message.caption,
        file_id=message.document.file_id
    )
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()


@dp.message_handler(content_types=[ContentType.PHOTO], state=SEND_MESSAGE)
async def send_message_confirmed_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text, k = await dh.send_message_confirmed(
        message.from_user.id,
        data['user_id'],
        message.caption,
        photo_id=message.photo[0].file_id
    )
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()


@dp.message_handler(lambda msg: len(msg.text) > 0, state=SEND_MESSAGE)
async def send_message_confirmed(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text, k = await dh.send_message_confirmed(message.from_user.id, data['user_id'], message.text)
    await send_message(text=text, chat_id=message.from_user.id, reply_markup=k)
    await state.reset_state()
