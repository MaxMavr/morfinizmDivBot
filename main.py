from config import *

btn: KeyboardButton = KeyboardButton(
    text='Гадать 💭')
kb_btn: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[btn]], resize_keyboard=True)

with open(f'{os.path.dirname(__file__)}/phrases.json', 'r', encoding="utf-8") as file:
    phrases = json.load(file)


async def logging(command, username, userid, *arg):
    if f'_{command}' in phrases:
        await bot.send_message(chat_id=MAIN_ADMIN_ID,
                               text=f"{phrases[f'_{command}']}\n"
                                    f"{username}\n"
                                    f"<code>{userid}</code>\n"
                                    f"{arg if arg else ''}")
    else:
        await bot.send_message(chat_id=MAIN_ADMIN_ID,
                               text=f"{command}\n"
                                    f"{username}\n"
                                    f"<code>{userid}</code>\n"
                                    f"{arg if arg else ''}")

    print(f"{command.upper()} {username} ({userid}) {arg if arg else ''}")


async def default_msg(message):
    await message.answer(
        phrases["hz_answers"][randint(0, len(phrases["hz_answers"]) - 1)],
        reply_markup=kb_btn)


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
        return await self.check(message.from_user.id)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    with sqlite3.connect(USERS_DB) as users_db:
        users_cursor = users_db.cursor()
        users_cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (message.from_user.id,))
        if users_cursor.fetchone()[0] > 0:
            await message.answer(text=phrases["old_id"], reply_markup=kb_btn)
        else:
            await message.answer(text=phrases["new_id"], reply_markup=kb_btn)

            users_cursor.execute(f'INSERT INTO users'
                                 f'(id, username)'
                                 f'VALUES (?, ?)',
                                 (message.from_user.id, message.from_user.username)
                                 )
            users_db.commit()


@dp.message(Command(commands='getusers'), Isadmin())
async def cmd_getusers(message: Message):
    with sqlite3.connect(USERS_DB) as users_db:
        users_cursor = users_db.cursor()
        users_cursor.execute(f'SELECT * FROM users ORDER BY isadmin')
        users = users_cursor.fetchall()

    msg = f'Всего пользователей {len(users)}\n\n'
    msg += '\n'.join(
        f'{user[1]} <code>{user[0]}</code>\n 🔢: {user[2]} 🏁: {user[3]}   {"👸" if user[4] == 1 else "🌫️"}' for user in users)
    await message.answer(msg)


@dp.message(Command(commands='getadmin'), Isadmin())  # /getadmin
async def cmd_getadmin(message: Message):
    with sqlite3.connect(USERS_DB) as users_db:
        users_cursor = users_db.cursor()
        users_cursor.execute(f'SELECT * FROM users WHERE isadmin = 1')
        admins = users_cursor.fetchall()

    msg = f'Всего админов {len(admins)}\n\n'
    msg += '\n'.join(f'{admin[1]} <code>{admin[0]}</code>' for admin in admins)
    await message.answer(msg)


@dp.message(Command(commands='getcircles'), Isadmin())
async def cmd_getcircles(message: Message):
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute(f'SELECT * FROM circles')
        circles = circles_cursor.fetchall()

    msg = f'Всего кружков {len(circles)}\n\n'
    msg += '\n'.join(f'<b>{circle[0]}</b>\n<code>{circle[1]}</code>' for circle in circles)
    await message.answer(msg)


@dp.message(Command(commands='root'))  # /root
async def cmd_setadmin(message: Message):
    if message.text[6:] == PASSWORD:
        with sqlite3.connect(USERS_DB) as users_db:
            users_cursor = users_db.cursor()
            users_cursor.execute("UPDATE users SET isadmin = ? WHERE id = ?", (1, message.from_user.id,))
            users_db.commit()

        await message.answer(phrases["right_password"])
        await logging('root', message.from_user.username, message.from_user.id)
    else:
        await message.answer(phrases["wrong_password"])


@dp.message(Command(commands='demote'), Isadmin())
async def cmd_demoteadmin(message: Message):
    with sqlite3.connect(USERS_DB) as users_db:
        users_cursor = users_db.cursor()
        users_cursor.execute("UPDATE users SET isadmin = ? WHERE id = ?", (0, message.from_user.id,))
        users_db.commit()

    await message.answer(phrases["revoke_admin"])
    await logging('demote', message.from_user.username, message.from_user.id)


@dp.message(Command(commands='fuck'), Isadmin())
async def cmd_deleteadmin(message: Message):
    userid = int(message.text[6:])
    if userid != MAIN_ADMIN_ID:
        with sqlite3.connect(USERS_DB) as users_db:
            users_cursor = users_db.cursor()
            users_cursor.execute("UPDATE users SET isadmin = ? WHERE id = ?", (0, userid,))
            users_db.commit()

        await bot.send_message(chat_id=userid,
                               text=phrases["fuck_admin"])
        await message.answer(phrases["delete_admin"])
        await logging('fuck', message.from_user.username, message.from_user.id)
    else:
        await message.answer("<b>Нельзя удалять главного админа!</b>\n"
                             "<i>Кстати, все твои приколы видно в логах, так что тебе жопа</i>")
        await logging('fuck! fuck! fuck!', message.from_user.username, message.from_user.id)


@dp.message(Command(commands='getcoms'), Isadmin())  # /getcoms
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
        "/morfinizm — работяги могут использовать в группах команду, чтобы бот отправил видик\n\n"
        "<i>Регистр для всех команд важен.\n"
        "Советую закрепить это сообщение, а не постоянно писать.\n"
        "Все ID и HASH кликабельны (Если они написаны моноширинным)</i>"
    )


@dp.message(F.video_note)
async def catch_text(message: Message):
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute(f'INSERT INTO circles'
                               f'(video_note)'
                               f'VALUES (?)',
                               (message.video_note.file_id,)
                               )
        circles_db.commit()

        circles_cursor.execute(f'SELECT number FROM circles WHERE video_note = ?', (message.video_note.file_id,))
        number = circles_cursor.fetchall()

    await message.answer(f'Кружок добавлен\n'
                         f'ID для удаления: <code>{str(number[0][0])}</code>')

    await logging('add', message.from_user.username, message.from_user.id)


@dp.message(Command(commands='del'))
async def cmd_start(message: Message):
    number = int(message.text[5:])
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute("SELECT number FROM circles")
        numbers = [i[0] for i in circles_cursor.fetchall()]

        if number in numbers:

            circles_cursor.execute(f'SELECT video_note FROM circles WHERE number = ?', (number,))
            video_note = circles_cursor.fetchall()[0][0]

            circles_cursor.execute('DELETE FROM circles WHERE number = ?', (number,))
            circles_db.commit()

            await logging('del', message.from_user.username, message.from_user.id, video_note)
        else:
            await message.answer(f'Нет кружка с ID {number}')


@dp.message(Command(commands='circle'))
async def cmd_chkcircles(message: Message):
    await bot.send_video_note(
        chat_id=message.chat.id,
        video_note=message.text[8:])


@dp.message(Command(commands='circleID'))
async def cmd_chkcircles(message: Message):
    number = int(message.text[10:])
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute("SELECT number FROM circles")
        numbers = [i[0] for i in circles_cursor.fetchall()]

        if number in numbers:

            circles_cursor.execute(f'SELECT video_note FROM circles WHERE number = ?', (number,))
            video_note = circles_cursor.fetchall()[0][0]

            await bot.send_video_note(
                chat_id=message.chat.id,
                video_note=video_note)
        else:
            await message.answer(f'Нет кружка с ID {number}')


@dp.message(Command(commands='about'))
async def cmd_about(message: Message):
    await message.answer(phrases["_about"])


@dp.message(Command(commands='help'))
async def cmd_help(message: Message):
    await message.answer(phrases["help"])


@dp.message(Command(commands='morfinizm'))  # /morfinizm
async def cmd_morfinizm(message: Message):
    await send_circle(chat_id = message.chat.id, user_id=message.from_user.id)


async def send_circle(chat_id: int, user_id: int):
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute("SELECT number FROM circles")
        number = [i[0] for i in circles_cursor.fetchall()]

        select_number = number[randint(0, len(number) - 1)]

        circles_cursor.execute(f'SELECT video_note FROM circles WHERE number = ?', (select_number,))
        video_note = circles_cursor.fetchall()[0][0]

    await bot.send_video_note(
        chat_id=chat_id,
        video_note=video_note)
    with sqlite3.connect(USERS_DB) as users_db:
        users_cursor = users_db .cursor()
        users_cursor.execute(
            "UPDATE users SET amount_divinations = amount_divinations + 1, last_divination = ? WHERE id = ?",
            (select_number, user_id))
        users_db.commit()


@dp.message(F.text)
async def catch_text(message: Message):
    if message.text.lower() in ['гадать', 'гадать 💭']:
        await send_circle(chat_id = message.chat.id, user_id=message.from_user.id)
    else:
        await default_msg(message)


@dp.message()
async def catch_default(message: Message):
    await default_msg(message)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Запустил гадалку")
    asyncio.run(main())
