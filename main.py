import asyncio
from aiogram import Dispatcher
from config_data.config import bot
from hadlers import user_handlers, admin_handlers, commands


async def main():
    dp = Dispatcher()

    dp.include_router(admin_handlers.router)
    dp.include_router(commands.router)
    dp.include_router(user_handlers.router)

    print('Запустил гадалку')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
