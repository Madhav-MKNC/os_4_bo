# -*- coding: utf-8 -*-
# author: Madhav Kumar (https://github.com/madhav-mknc/)

import os
import telebot
from telebot import types


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# STATE (per user)
# =========================
user_sessions = {}  
# user_id -> {
#   "active": bool,
#   "session_id": int
# }

# =========================
# BACKEND HOOKS (ALREADY EXIST)
# =========================
def process_chat_message(user_id: int, text: str, session_id: int):
    """
    Your backend processing function.
    Called for every message between /start and /end.
    """
    pass


def generate_result_image(user_id: int, session_id: int) -> str:
    """
    Generates JPG and returns absolute file path.
    """
    return "/absolute/path/to/generated.jpg"


# =========================
# COMMANDS
# =========================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    uid = message.from_user.id

    prev_session = user_sessions.get(uid, {}).get("session_id", 0)
    new_session_id = prev_session + 1

    user_sessions[uid] = {
        "active": True,
        "session_id": new_session_id
    }

    bot.reply_to(
        message,
        f"Listening started.\nSession ID: {new_session_id}"
    )


@bot.message_handler(commands=["end"])
def end_cmd(message):
    uid = message.from_user.id
    session = user_sessions.get(uid)

    if not session or not session["active"]:
        bot.reply_to(message, "No active session. Use /start first.")
        return

    session["active"] = False
    session_id = session["session_id"]

    img_path = generate_result_image(uid, session_id)

    with open(img_path, "rb") as img:
        bot.send_photo(
            message.chat.id,
            img,
            caption=f"Session {session_id} ended."
        )


# =========================
# MESSAGE LISTENER
# =========================
@bot.message_handler(func=lambda m: True, content_types=["text"])
def listen_messages(message):
    uid = message.from_user.id
    session = user_sessions.get(uid)

    if not session or not session["active"]:
        return

    process_chat_message(
        user_id=uid,
        text=message.text,
        session_id=session["session_id"]
    )


# =========================
# START BOT
# =========================
def bot_thread():
    print("[#] bot is online")
    # bot.polling()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    bot_thread()

