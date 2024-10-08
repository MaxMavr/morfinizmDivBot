from aiogram import Bot, Dispatcher
import os

# PHASALO ON
try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
    API_TOKEN: str = os.getenv('TOKEN')
    PASSWORD: str = os.getenv('PASSWORD')
    MAIN_ADMIN_ID: int = int(os.getenv('MAIN_ADMIN_ID'))
    BOT_ID: int = int(os.getenv('BOT_ID'))
except Exception:
    from API_TOKEN import *

try:
    bot: Bot = Bot(token=API_TOKEN, parse_mode='HTML')
except Exception:
    from aiogram.client.default import DefaultBotProperties

    bot: Bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
# PHASALO OFF


dp: Dispatcher = Dispatcher()
