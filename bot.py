# bot.py
import os
import logging
import requests
from urllib.parse import unquote
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("https://shop-miniapp.onrender.com")
API_URL = os.getenv("API_URL") or f"https://shop-miniapp.onrender.com/api/save-user"

# --- логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- создаём Application глобально ---
application = Application.builder().token(TELEGRAM_TOKEN).build()


# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        arg = args[0]
        if arg.startswith("webapp_auth"):
            return await handle_webapp_auth(update, arg)
        elif arg.startswith("complete_profile"):
            return await handle_complete_profile(update)
    await show_main_menu(update)

async def handle_webapp_auth(update: Update, arg: str):
    return_url = unquote(arg.split("_", 2)[-1]) if "_" in arg else WEB_APP_URL
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=return_url))]
    ]
    await update.message.reply_text(
        "Для авторизации поделитесь номером:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_complete_profile(update: Update):
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("✏️ Ввести имя")]
    ]
    await update.message.reply_text(
        "Пожалуйста, дополните профиль: отправьте имя или номер телефона.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    data = {
        "id": user.id,
        "first_name": user.first_name or contact.first_name,
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": contact.phone_number,
        "auth_date": update.message.date.timestamp()
    }
    try:
        r = requests.post(API_URL, json=data)
        if r.ok:
            await update.message.reply_text("✅ Ваш номер сохранён!")
        else:
            await update.message.reply_text("⚠️ Ошибка при сохранении.")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await update.message.reply_text("Произошла ошибка.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    data = {
        "id": user.id,
        "first_name": text,
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": "не указан",
        "auth_date": update.message.date.timestamp()
    }
    try:
        r = requests.post(API_URL, json=data)
        if r.ok:
            await update.message.reply_text(f"✅ Имя {text} сохранено!")
        else:
            await update.message.reply_text("⚠️ Ошибка при сохранении.")
    except Exception as e:
        logger.error(f"Ошибка имени: {e}")
        await update.message.reply_text("Произошла ошибка.")

async def show_main_menu(update: Update):
    await update.message.reply_text("Добро пожаловать! Используйте WebApp для входа.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Ошибка:", exc_info=context.error)

# --- регистрируем обработчики ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_error_handler(error_handler)
