
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, Dispatcher
from flask import Flask, request
import requests
import os

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
LANGFLOW_API = os.environ["LANGFLOW_API_URL"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=1, use_context=True)

def handle_message(update: Update, context: CallbackContext):
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
