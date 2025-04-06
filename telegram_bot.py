
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, Dispatcher
from flask import Flask, request
import requests
import os
import logging
import json
from datetime import datetime

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
LANGFLOW_API = os.environ["LANGFLOW_API_URL"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)

logging.basicConfig(level=logging.INFO)

def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "no_username"

    # Собираем данные в структуру
    full_payload = {
        "event": "telegram_request",
        "user_id": user_id,
        "username": username,
        "message": user_text,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Логируем
    logging.info(json.dumps(full_payload))

    # Отправляем полные данные в Langflow
    payload = {
        "inputs": {
            "input": json.dumps(full_payload)
        }
    }

    try:
        res = requests.post(LANGFLOW_API, json=payload)
        res.raise_for_status()
        reply = res.json()["data"][0]

        logging.info(json.dumps({
            "event": "langflow_response",
            "user_id": user_id,
            "response": reply,
            "timestamp": datetime.utcnow().isoformat()
        }))

        update.message.reply_text(reply)

    except Exception as e:
        logging.error(json.dumps({
            "event": "error",
            "user_id": user_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }))
        update.message.reply_text("Ошибка: " + str(e))

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Бот работает."

if __name__ == "__main__":
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
