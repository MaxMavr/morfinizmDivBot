import sqlite3
import os
from collections import defaultdict
from typing import List, Tuple

USERS_DB = f'{os.path.dirname(__file__)}/DB/users.db'
CIRCLES_DB = f'{os.path.dirname(__file__)}/DB/circles.db'

con = sqlite3.connect(USERS_DB)
cursor_usersDB = con.cursor()

cursor_usersDB.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY NOT NULL,
        username TEXT NOT NULL DEFAULT 'username',
        amount_divinations INTEGER NOT NULL DEFAULT 0,
        last_divination INTEGER,
        isadmin INTEGER CHECK (isadmin IN (0, 1)) NOT NULL DEFAULT 0
    )
''')
cursor_usersDB.close()
con.close()

con = sqlite3.connect(CIRCLES_DB)
cursor_circlesDB = con.cursor()
cursor_circlesDB.execute('''
    CREATE TABLE IF NOT EXISTS circles (
        number INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        video_note TEXT NOT NULL DEFAULT 'AAA'
    )
''')
cursor_circlesDB.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        video_number INTEGER NOT NULL,
        chat_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        FOREIGN KEY (video_number) REFERENCES circles(number),
        UNIQUE (chat_id, message_id)
    );
''')
cursor_circlesDB.close()
con.close()


class VideoMessage:
    def __init__(self, chat_id: int, message_ids: List[int]):
        self.chat_id = chat_id
        self.message_ids = message_ids


def fetch_user_count(user_id: int) -> int:
    with sqlite3.connect(USERS_DB) as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()[0]


def insert_user(user_id: int, username: str):
    with sqlite3.connect(USERS_DB) as db:
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (id, username) VALUES (?, ?)', (user_id, username))
        db.commit()


def insert_circle(circle_file_id: str):
    with sqlite3.connect(CIRCLES_DB) as db:
        cursor = db.cursor()
        cursor.execute(f'INSERT INTO circles'
                       f'(video_note)'
                       f'VALUES (?)',
                       (circle_file_id,)
                       )
        db.commit()
        cursor.execute(f'SELECT number FROM circles WHERE video_note = ?', (circle_file_id,))
        return cursor.fetchall()


def fetch_all_users() -> List[Tuple]:
    with sqlite3.connect(USERS_DB) as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users ORDER BY isadmin')
        return cursor.fetchall()


def fetch_all_admins() -> List[Tuple]:
    with sqlite3.connect(USERS_DB) as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE isadmin = 1')
        return cursor.fetchall()


def update_user_admin_status(user_id: int, is_admin: int):
    with sqlite3.connect(USERS_DB) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET isadmin = ? WHERE id = ?", (is_admin, user_id))
        db.commit()


def update_user_divination(user_id: int, select_number: int):
    with sqlite3.connect(USERS_DB) as users_db:
        users_cursor = users_db.cursor()
        users_cursor.execute(
            "UPDATE users SET amount_divinations = amount_divinations + 1, last_divination = ? WHERE id = ?",
            (select_number, user_id))
        users_db.commit()


def get_circle_numbers():
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute("SELECT number FROM circles")
        return [i[0] for i in circles_cursor.fetchall()]


def fetch_all_circles() -> List[Tuple]:
    with sqlite3.connect(CIRCLES_DB) as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM circles')
        return cursor.fetchall()


def get_video_note(number):
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute("SELECT video_note FROM circles WHERE number = ?", (number,))
        result = circles_cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return None


def get_video_number(video_hash):
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute("SELECT number FROM circles WHERE video_note = ?", (video_hash,))
        result = circles_cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            return None


def delete_circle(number):
    with sqlite3.connect(CIRCLES_DB) as circles_db:
        circles_cursor = circles_db.cursor()
        circles_cursor.execute('DELETE FROM circles WHERE number = ?', (number,))
        circles_db.commit()


def add_message(video_number: int, chat_id: int, message_id: int) -> None:
    conn = sqlite3.connect(CIRCLES_DB)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO messages (video_number, chat_id, message_id)
            VALUES (?, ?, ?)
        ''', (video_number, chat_id, message_id))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Сообщение-кружок: {video_number}-{chat_id}-{message_id} уже существует в базе данных.")
    finally:
        conn.close()


def get_messages_for_video(video_number: int) -> List[VideoMessage]:
    conn = sqlite3.connect(CIRCLES_DB)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT chat_id, message_id
        FROM messages
        WHERE video_number = ?
    ''', (video_number,))

    messages_info = cursor.fetchall()
    conn.close()

    # Группируем message_id по chat_id
    grouped_messages = defaultdict(list)
    for chat_id, message_id in messages_info:
        grouped_messages[chat_id].append(message_id)

    # Преобразуем в список объектов Video_message
    result = [VideoMessage(chat_id=chat_id, message_ids=message_ids) for chat_id, message_ids in grouped_messages.items()]

    return result


if __name__ == '__main__':
    pass
