from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from db_interface import *
from filters import filters
from config_data.config import MAIN_ADMIN_ID, bot
from lexicon.lexicon_ru import phrases
from logging_data.logging import logging

router = Router()
router.message.filter(filters.Isadmin())


@router.message(Command(commands='getusers'))  # /getusers
async def cmd_getusers(message: Message):
    users = fetch_all_users()
    msg = f'Всего пользователей {len(users)}\n\n'
    msg += '\n'.join(
        f'{user[1]} <code>{user[0]}</code>\n 🔢: {user[2]} 🏁: {user[3]}   {"👸" if user[4] == 1 else "🌫️"}' for user in users)
    await message.answer(msg)


@router.message(Command(commands='getadmin'))  # /getadmin
async def cmd_getadmin(message: Message):
    admins = fetch_all_admins()
    msg = f'Всего админов {len(admins)}\n\n'
    msg += '\n'.join(f'{admin[1]} <code>{admin[0]}</code>' for admin in admins)
    await message.answer(msg)


@router.message(Command(commands='getcircles'))  # /getcircles
async def cmd_getcircles(message: Message):
    circles = fetch_all_circles()
    msg = f'Всего кружков {len(circles)}\n\n'
    msg += '\n'.join(f'<b>{circle[0]}</b>\n<code>{circle[1]}</code>' for circle in circles)
    await message.answer(msg)


@router.message(Command(commands='demote'))  # /demote
async def cmd_demoteadmin(message: Message):
    update_user_admin_status(message.from_user.id, 0)
    await message.answer(phrases["revoke_admin"])
    await logging('demote', message.from_user.username, message.from_user.id)


@router.message(Command(commands='fuck'))  # /fuck
async def cmd_deleteadmin(message: Message):
    userid = int(message.text[6:])
    if userid != MAIN_ADMIN_ID:
        if fetch_user_count(message.from_user.id) > 0 and filters.Isadmin.check(userid):
            update_user_admin_status(userid, 0)
            await bot.send_message(chat_id=userid, text=phrases["fuck_admin"])
            await message.answer(phrases["delete_admin"])
            await logging('fuck', message.from_user.username, message.from_user.id)
        else:
            await message.answer('Пользователя с таким id не существует или пользователь не является админом')
    else:
        await message.answer("<b>Нельзя удалять главного админа!</b>\n"
                             "<i>Кстати, все твои приколы видно в логах, так что тебе жопа</i>")
        await logging('fuck! fuck! fuck!', message.from_user.username, message.from_user.id)


@router.message(Command(commands='getcoms'))  # /getcoms
async def cmd_getcom(message: Message):
    await message.answer(
        "<b>Посмотреть</b>\n"
        "/getusers — пользователей\n"
        "/getadmin — админов\n"
        "/getcircles — кружки\n"
        "/circle {hash} — кружок\n"
        "/circleID {id} — кружок по АйДишнику\n\n"
        "<b>Работа с кружками</b>\n"
        "Добавить кружок легко, либо записать прямо в бота, либо переслать. "
        "Любой кружок попавший в чат от админа сразу записывается в БД\n"
        "/del {id} — удалить кружок\n"
        "<b>Для управления админами</b>\n"
        "/root {пароль} — стать админом\n"
        "/demote — разжаловаться\n"
        "/fuck {id} — разжаловать\n"
        "/getcoms — посмотреть команды (Это сообщение)\n\n"
        "<b>Для плебса</b>\n"
        "/start — старт, есть старт\n"
        "/about — информация о боте\n"
        "/help — как пользоваться\n"
        "/morfinizm — команда для работяг, отправляющая в чатик рандомный видик\n\n"
        "<i>Регистр для всех команд важен.\n"
        "Советую закрепить это сообщение, а не постоянно писать.\n"
        "Все ID и HASH кликабельны (Если они написаны моноширинным)</i>"
    )
