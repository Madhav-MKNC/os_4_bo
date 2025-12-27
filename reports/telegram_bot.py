# -*- coding: utf-8 -*-
# author: Madhav Kumar (https://github.com/madhav-mknc/)

import os
import json
import telebot
from telebot import types
import threading

from configs import OUTPUT_FOLDER
from .daily_reports import generate_daily_report


FILE_LOCK = threading.Lock()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHAT_ID = "-1003506079975"
CHATS_FILE = "chats.json"

# def read_chats() -> list:
#     with open(CHATS_FILE, 'r', encoding='utf-8') as file:
#         chats = json.load(file)
#     return chats

# def add_chats(text):
#     chats = read_chats()
#     chats.append(text)
#     write_chats(chats)

# def write_chats(chats=[]):
#     with open(CHATS_FILE, 'w', encoding='utf-8') as file:
#         json.dump(chats, file)

def read_chats() -> list:
    with FILE_LOCK:
        with open(CHATS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)

def write_chats(chats):
    with FILE_LOCK:
        with open(CHATS_FILE, 'w', encoding='utf-8') as file:
            json.dump(chats, file, ensure_ascii=False)

def add_chats(text):
    with FILE_LOCK:
        with open(CHATS_FILE, 'r+', encoding='utf-8') as file:
            chats = json.load(file)
            chats.append(text)
            file.seek(0)
            json.dump(chats, file, ensure_ascii=False)
            file.truncate()

if not os.path.exists(CHATS_FILE):
    write_chats(chats=[])

# =========================
# COMMANDS
# =========================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    uid = message.chat.id
    print(uid)
    if str(uid).strip() != CHAT_ID:
        return

    write_chats(chats=[])

    bot.reply_to(
        message,
        f"Listening started. \nSend below all the reports."
    )


@bot.message_handler(commands=["end", "get", "generate"])
def end_cmd(message):
    uid = message.chat.id
    print(uid)
    if str(uid).strip() != CHAT_ID:
        return

    chats = read_chats()
    if not chats:
        bot.reply_to(message, "No active session.")
        return

    bot.reply_to(
        message,
        f"Generating with len(chats)={len(chats)}"
    )

    img_name = generate_daily_report(
        chats=chats,
        output_folder=OUTPUT_FOLDER
    )
    img_path = os.path.join(OUTPUT_FOLDER, img_name)

    write_chats(chats=[])

    with open(img_path, "rb") as img:
        bot.send_photo(
            message.chat.id,
            img,
            caption=f"Session Refreshed."
        )


@bot.message_handler(commands=["status"])
def status_cmd(message):
    uid = message.chat.id
    print(uid)
    if str(uid).strip() != CHAT_ID:
        return

    chats = read_chats()

    bot.reply_to(
        message,
        f"Total Chats: {len(chats)}"
    )


# =========================
# MESSAGE LISTENER
# =========================
@bot.message_handler(
    content_types=["text"],
    chat_types=["group", "supergroup"]
)
def listen_messages(message):
    uid = message.chat.id
    print(uid)
    if str(uid).strip() != CHAT_ID:
        return

    text = message.text
    print(len(text))

    if message.text.startswith("/"):
        return  # ignore commands

    add_chats(text)


# =========================
# START BOT
# =========================
def bot_thread():
    print("[#] bot is online")
    # bot.polling()
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    bot_thread()

