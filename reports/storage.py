import os
import json
from typing import Dict, List


class Chats:
    def __init__(self, filename='chats.json'):
        self.filename = filename
        self.chats: Dict[str, List[Dict]] = {}
        self.load_chats()

    def get_chat(self, chat_id):
        return self.chats.get(chat_id, [])

    def add_message(self, chat_id, message):
        if chat_id not in self.chats:
            self.chats[chat_id] = []
        self.chats[chat_id].append(message)
        self.write_chats()

    def load_chats(self, filename='chats.json'):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.chats = json.load(f)
        return self.chats

    def write_chats(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.chats, f)


