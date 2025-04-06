
from telegram.ext import Updater, MessageHandler, Filters
import requests
import os

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
LANGFLOW_API = os.environ["LANGFLOW_API_URL"]

def handle_message(update, context):
    user_text = update.message.text

    payload = {
        "inputs": {
            "input": user_text
        }
    }

    try:
        res = requests.post(LANGFLOW_API, json=payload)
        reply = res.json()["data"][0]
        update.message.reply_text(reply)
    except Exception as e:
        update.message.reply_text("Ошибка: " + str(e))

updater = Updater(BOT_TOKEN)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
updater.start_polling()
updater.idle()
