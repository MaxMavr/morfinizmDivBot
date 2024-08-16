import asyncio
import sqlite3
from random import randint
import os
import json

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, BaseFilter
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

USERS_DB = f'{os.path.dirname(__file__)}/DB/users.db'
CIRCLES_DB = f'{os.path.dirname(__file__)}/DB/circles.db'

con = sqlite3.connect(USERS_DB)
cursor = con.cursor()

cursor.execute(
    '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY NOT NULL,
            username TEXT NOT NULL DEFAULT 'username',
            amount_divinations INTEGER NOT NULL DEFAULT 0,
            last_divination INTEGER,
            isadmin INTEGER CHECK (isadmin IN (0, 1)) NOT NULL DEFAULT 0
    )''')
cursor.close()
con.close()

con = sqlite3.connect(CIRCLES_DB)
cursor = con.cursor()
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS circles (
            number INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            video_note TEXT NOT NULL DEFAULT 'AAA'
    )''')
cursor.close()
con.close()

# PHASALO ON
try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    API_TOKEN: str = os.getenv('TOKEN')
    PASSWORD: str = os.getenv('PASSWORD')
    MAIN_ADMIN_ID: int = int(os.getenv('MAIN_ADMIN_ID'))
except Exception:
    from API_TOKEN import *

try:
    bot: Bot = Bot(token=API_TOKEN, parse_mode='HTML')
except Exception:
    from aiogram.client.default import DefaultBotProperties

    bot: Bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
# PHASALO OFF


dp: Dispatcher = Dispatcher()
