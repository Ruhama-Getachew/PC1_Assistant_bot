ASKING_NAME, ASKING_ID = range(2)
import os
from telegram import Update
from database.db import is_already_registered, insert_registration, check_roster
from telegram.ext import ContextTypes, ConversationHandler

GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to PC1 Assistant!\n\nIf you haven't joined the group yet, use /join to register."
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send your full name.")
    return ASKING_NAME
    

async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Thanks. Now please send your student ID.")
    return ASKING_ID

async def verify_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_id = update.message.text
    name = context.user_data["name"]
    telegram_user_id = update.effective_user.id

    if is_already_registered(telegram_user_id):
        await update.message.reply_text(
            "You're already registered. If this is a mistake, contact the rep."
        )
        return ConversationHandler.END

    if not check_roster(student_id):
        await update.message.reply_text(
            "Wrong input. Please check your student ID and send it again."
        )
        return ASKING_ID  # stay in this state, let them retry

    insert_registration(name, student_id, telegram_user_id)

    invite_link = await context.bot.create_chat_invite_link(
        chat_id=int(GROUP_CHAT_ID),       # your group's chat ID
        member_limit=1
    )
    await update.message.reply_text(f"Verified! Here's your invite link: {invite_link.invite_link}")
    return ConversationHandler.END

