from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from config_data.config import PASSWORD, bot
from db_interface import *
from hadlers.user_handlers import send_circle
from keyboards.user_keyboards import kb_btn
from lexicon.lexicon_ru import phrases
from logging_data.logging import logging

router = Router()


@router.message(CommandStart())  # /start
async def cmd_start(message: Message):
    user_count = fetch_user_count(message.from_user.id)
    if user_count > 0:
        await message.answer(text=phrases["old_id"], reply_markup=kb_btn)
    else:
        await message.answer(text=phrases["new_id"], reply_markup=kb_btn)
        insert_user(message.from_user.id, message.from_user.username)


@router.message(Command(commands='root'))  # /root
async def cmd_root(message: Message):
    if message.text[6:] == PASSWORD:
        update_user_admin_status(message.from_user.id, 1)
        await message.answer(phrases["right_password"])
        await logging('root', message.from_user.username, message.from_user.id)
    else:
        await message.answer(phrases["wrong_password"])


@router.message(Command(commands='del'))  # /del
async def cmd_del(message: Message):
    number = int(message.text[5:])
    numbers = get_circle_numbers()

    if number in numbers:
        video_note = get_video_note(number)
        delete_circle(number)
        message_list = get_messages_for_video(number)
        for messages in message_list:
            try:
                await bot.delete_messages(chat_id=messages.chat_id, message_ids=messages.message_ids)
            except Exception as e:
                print(e)
        await logging('del', message.from_user.username, message.from_user.id, video_note)
    else:
        await message.answer(f'Нет кружка с ID {number}')


@router.message(Command(commands='circle'))  # /circle
async def cmd_chkcircles(message: Message):
    video_hash = message.text[8:]
    number = get_video_number(video_hash)
    if number:
        msg = await bot.send_video_note(chat_id=message.chat.id, video_note=video_hash)
        add_message(number, msg.chat.id, msg.message_id)
    else:
        await message.answer('Кружка с таким хэшем нет')


@router.message(Command(commands='circleID'))  # /circleID
async def cmd_chkcircles(message: Message):
    number = int(message.text[10:])
    numbers = get_circle_numbers()

    if number in numbers:
        video_note = get_video_note(number)
        msg = await bot.send_video_note(chat_id=message.chat.id, video_note=video_note)
        add_message(number, msg.chat.id, msg.message_id)
    else:
        await message.answer(f'Нет кружка с ID {number}')


@router.message(Command(commands='about'))  # /about
async def cmd_about(message: Message):
    await message.answer(phrases["_about"])


@router.message(Command(commands='help'))  # /help
async def cmd_help(message: Message):
    await message.answer(phrases["help"])


@router.message(Command(commands='morfinizm'))  # /morfinizm
async def cmd_morfinizm(message: Message):
    await send_circle(chat_id=message.chat.id, user_id=message.from_user.id)
