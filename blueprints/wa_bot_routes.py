from flask import Flask, Blueprint, jsonify, render_template, request
import requests
import os


wa_bot_routes = Blueprint('wa_bot_routes', __name__)


TOKEN = os.environ["WA_TOKEN"]
PHONE_ID = os.environ["WA_PHONE_ID"]


MESSAGES = []  # in-memory log


def send(to, text):
    requests.post(
        f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": text}
        }
    )


@wa_bot_routes.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == os.environ["VERIFY_TOKEN"]:
            return challenge, 200
        return "forbidden", 403

    msg = request.json["entry"][0]["changes"][0]["value"]["messages"][0]
    text = msg["text"]["body"]
    user = msg["from"]

    MESSAGES.append(f"{user}: {text}")

    if text.strip().lower() == "/all":
        reply = "\n".join(MESSAGES) or "No messages yet"
    else:
        reply = "ok"

    send(user, reply)
    return "ok"

