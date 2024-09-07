from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

btn: KeyboardButton = KeyboardButton(
    text='Гадать 💭')
kb_btn: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[btn]], resize_keyboard=True)
