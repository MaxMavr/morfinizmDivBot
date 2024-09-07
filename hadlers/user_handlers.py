from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message
import random
from config_data.config import bot, BOT_ID
from db_interface import *
from keyboards.user_keyboards import kb_btn
from lexicon.lexicon_ru import phrases
from logging_data.logging import logging

router = Router()


async def default_msg(message):
    await message.answer(
        phrases["hz_answers"][random.randint(0, len(phrases["hz_answers"]) - 1)],
        reply_markup=kb_btn)


@router.message(F.video_note)
async def catch_video_note(message: Message):
    number = insert_circle(message.video_note.file_id)

    await message.answer(f'Кружок добавлен\n'
                         f'ID для удаления: <code>{str(number[0][0])}</code>')

    await logging('add', message.from_user.username, message.from_user.id)


async def send_circle(chat_id: int, user_id: int):
    numbers = get_circle_numbers()

    select_number = random.choice(numbers)
    video_note = get_video_note(select_number)

    msg = await bot.send_video_note(chat_id=chat_id, video_note=video_note)
    add_message(select_number, msg.chat.id, msg.message_id)

    update_user_divination(user_id, select_number)


@router.message(F.text)
async def catch_text(message: Message):
    if message.text.lower() in ['гадать', 'гадать 💭']:
        await send_circle(chat_id=message.chat.id, user_id=message.from_user.id)
    else:
        await default_msg(message)


@router.message(F.content_type.in_({ContentType.TEXT,
                                    ContentType.PHOTO,
                                    ContentType.VOICE,
                                    ContentType.VIDEO}))
async def catch_default(message: Message):
    await default_msg(message)


@router.message()
async def invited_in(message: Message):
    if message.new_chat_members:
        print(message.new_chat_members)
        if message.new_chat_members[0].id == BOT_ID:
            await message.answer('Приветствую фанатов Морфнизма пыльцы!')
