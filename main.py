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
        if message.chat.type != 'private':
            return False
        return await self.check(message.from_user.id)


@dp.message(CommandStart())  # /start
async def cmd_start(message: Message):
    user_count = fetch_user_count(message.from_user.id)
    if user_count > 0:
        await message.answer(text=phrases["old_id"], reply_markup=kb_btn)
    else:
        await message.answer(text=phrases["new_id"], reply_markup=kb_btn)
        insert_user(message.from_user.id, message.from_user.username)


@dp.message(Command(commands='getusers'), Isadmin())  # /getusers
async def cmd_getusers(message: Message):
    users = fetch_all_users()
    msg = f'Всего пользователей {len(users)}\n\n'
    msg += '\n'.join(
        f'{user[1]} <code>{user[0]}</code>\n 🔢: {user[2]} 🏁: {user[3]}   {"👸" if user[4] == 1 else "🌫️"}' for user in users)
    await message.answer(msg)


@dp.message(Command(commands='getadmin'), Isadmin())  # /getadmin
async def cmd_getadmin(message: Message):
    admins = fetch_all_admins()
    msg = f'Всего админов {len(admins)}\n\n'
    msg += '\n'.join(f'{admin[1]} <code>{admin[0]}</code>' for admin in admins)
    await message.answer(msg)


@dp.message(Command(commands='getcircles'), Isadmin())  # /getcircles
async def cmd_getcircles(message: Message):
    circles = fetch_all_circles()
    msg = f'Всего кружков {len(circles)}\n\n'
    msg += '\n'.join(f'<b>{circle[0]}</b>\n<code>{circle[1]}</code>' for circle in circles)
    await message.answer(msg)


@dp.message(Command(commands='root'))  # /root
async def cmd_root(message: Message):
    if message.text[6:] == PASSWORD:
        update_user_admin_status(message.from_user.id, 1)
        await message.answer(phrases["right_password"])
        await logging('root', message.from_user.username, message.from_user.id)
    else:
        await message.answer(phrases["wrong_password"])


@dp.message(Command(commands='demote'), Isadmin())  # /demote
async def cmd_demoteadmin(message: Message):
    update_user_admin_status(message.from_user.id, 0)
    await message.answer(phrases["revoke_admin"])
    await logging('demote', message.from_user.username, message.from_user.id)


@dp.message(Command(commands='fuck'), Isadmin())  # /fuck
async def cmd_deleteadmin(message: Message):
    userid = int(message.text[6:])
    if userid != MAIN_ADMIN_ID:
        if fetch_user_count(message.from_user.id) > 0 and Isadmin.check(userid):
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
        "/morfinizm — команда для работяг, отправляющая в чатик рандомный видик\n\n"
        "<i>Регистр для всех команд важен.\n"
        "Советую закрепить это сообщение, а не постоянно писать.\n"
        "Все ID и HASH кликабельны (Если они написаны моноширинным)</i>"
    )


@dp.message(F.video_note)
async def catch_video_note(message: Message):
    number = insert_circle(message.video_note.file_id)

    await message.answer(f'Кружок добавлен\n'
                         f'ID для удаления: <code>{str(number[0][0])}</code>')

    await logging('add', message.from_user.username, message.from_user.id)


@dp.message(Command(commands='del'))  # /del
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


@dp.message(Command(commands='circle'))  # /circle
async def cmd_chkcircles(message: Message):
    video_hash = message.text[8:]
    number = get_video_number(video_hash)
    if number:
        msg = await bot.send_video_note(chat_id=message.chat.id, video_note=video_hash)
        add_message(number, msg.chat.id, msg.message_id)
    else:
        await message.answer('Кружка с таким хэшем нет')


@dp.message(Command(commands='circleID'))  # /circleID
async def cmd_chkcircles(message: Message):
    number = int(message.text[10:])
    numbers = get_circle_numbers()

    if number in numbers:
        video_note = get_video_note(number)
        msg = await bot.send_video_note(chat_id=message.chat.id, video_note=video_note)
        add_message(number, msg.chat.id, msg.message_id)
    else:
        await message.answer(f'Нет кружка с ID {number}')


@dp.message(Command(commands='about'))  # /about
async def cmd_about(message: Message):
    await message.answer(phrases["_about"])


@dp.message(Command(commands='help'))  # /help
async def cmd_help(message: Message):
    await message.answer(phrases["help"])


@dp.message(Command(commands='morfinizm'))  # /morfinizm
async def cmd_morfinizm(message: Message):
    await send_circle(chat_id=message.chat.id, user_id=message.from_user.id)


async def send_circle(chat_id: int, user_id: int):
    numbers = get_circle_numbers()

    select_number = random.choice(numbers)
    video_note = get_video_note(select_number)

    msg = await bot.send_video_note(chat_id=chat_id, video_note=video_note)
    add_message(select_number, msg.chat.id, msg.message_id)

    update_user_divination(user_id, select_number)


@dp.message(F.text)
async def catch_text(message: Message):
    if message.text.lower() in ['гадать', 'гадать 💭']:
        await send_circle(chat_id=message.chat.id, user_id=message.from_user.id)
    else:
        await default_msg(message)


@dp.message(F.content_type.in_({ContentType.TEXT,
                                ContentType.PHOTO,
                                ContentType.VOICE,
                                ContentType.VIDEO}))
async def catch_default(message: Message):
    await default_msg(message)


@dp.message()
async def invited_in(message: Message):
    if message.new_chat_members:
        print(message.new_chat_members)
        if message.new_chat_members[0].id == BOT_ID:
            await message.answer('Приветствую фанатов Морфнизма пыльцы!')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Запустил гадалку")
    asyncio.run(main())
