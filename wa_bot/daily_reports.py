import zipfile
import os
import re


def build_messages(chat_log):
    newline_index = chat_log.find('\n')
    if newline_index != -1:
        chat_log = chat_log[newline_index + 1:]
    chat_log = chat_log.replace('\u202f', ' ')
    pattern = r"(?i)(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?: (?:am|pm))? -)"
    split_log = re.split(pattern, chat_log)
    messages_list = []
    for i in range(0, len(split_log), 2):
        log = split_log[i]
        if log and ":" in log:
            message = log[log.find(':') + 1:].strip()
            messages_list.append(message)
    return messages_list

def read_whatsapp_zip(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            txt_files = [f for f in file_list if f.endswith('.txt')]
            if not txt_files:
                print("No text file found in the zip archive")
                return None, None
            chat_file = txt_files[0]
            with zip_ref.open(chat_file) as f:
                try:
                    chat_text = f.read().decode('utf-8')
                except UnicodeDecodeError:
                    chat_text = f.read().decode('utf-8', errors='ignore')
            messages = build_messages(chat_text)
            return chat_text, messages
    except FileNotFoundError:
        print(f"Error: File '{zip_path}' not found")
        return None, None
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid zip file")
        return None, None
    return raw_text, messages


def generate_daily_report(zip_file_path):
    _, messages = read_whatsapp_zip()
    return f"len(messages)={len(messages)}"


if __name__ == "__main__":
    zip_file_path = "wa chats.zip"
    raw_text, messages = read_whatsapp_zip(zip_file_path)
    if messages:
        for msg in messages:
            print(f"\n{msg}\n")
    else:
        print("No messages to display")

