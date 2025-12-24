import os
import json 


# class Storage:
#     def __init__(self, filename='storage.json'):
#         self.filename = filename
#         self.data = self._load()

#     def _load(self):
#         if os.path.exists(self.filename):
#             with open(self.filename, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         return {}

#     def save(self):
#         with open(self.filename, 'w', encoding='utf-8') as f:
#             json.dump(self.data, f)

#     def get(self, key, default=None):
#         return self.data.get(key, default)

#     def set(self, key, value):
#         self.data[key] = value
#         self.save()


# this will be used for storing the conversations and making the bot stateful
class Chats:
    def __init__(self):
        self.chats = {}

    def get_chat(self, chat_id):
        return self.chats.get(chat_id, [])

    def add_message(self, chat_id, message):
        if chat_id not in self.chats:
            self.chats[chat_id] = []
        self.chats[chat_id].append(message)

    def read_storage(self, filename='chats.json'):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.chats = json.load(f)

    def write_storage(self, filename='chats.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.chats, f)
chats = Chats()


