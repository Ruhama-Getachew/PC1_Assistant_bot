import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters

from handlers.register import start, join, ask_id, verify_id, ASKING_NAME, ASKING_ID

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

load_dotenv()

def main():
    telegram_app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("join", join)],
    states={
        ASKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_id)],
        ASKING_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_id)],
    },
    fallbacks=[CommandHandler("join", join)],  # allows restart mid-conversation
    allow_reentry=True,                         # key fix
)

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(conv_handler)

    telegram_app.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    import time; time.sleep(1)
    main()