from aiogram.filters import BaseFilter
import sqlite3
from aiogram.types import Message
from db_interface import USERS_DB


class Isadmin(BaseFilter):
    @staticmethod
    async def check(id) -> bool:
        with sqlite3.connect(USERS_DB) as users_db:
            users_cursor = users_db.cursor()
            users_cursor.execute("SELECT isadmin FROM users WHERE id = ?", (id,))
            isadmin_number = users_cursor.fetchall()

            if isadmin_number:
                return isadmin_number[0][0] == 1
        return False

    async def __call__(self, message: Message) -> bool:
        if message.chat.type != 'private':
            return False
        return await self.check(message.from_user.id)
