from config_data.config import MAIN_ADMIN_ID, bot
from lexicon.lexicon_ru import phrases


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
