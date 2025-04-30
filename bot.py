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

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL") or "https://shop-miniapp.onrender.com"
API_URL = os.getenv("API_URL", f"https://shop-miniapp.onrender.com/api/save-user")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or f"https://shop-miniapp.onrender.com/webhook"

# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Обработчики ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        param = args[0]
        if param.startswith("webapp_auth"):
            return await handle_webapp_auth(update, param)
        elif param.startswith("complete_profile"):
            return await handle_complete_profile(update)
    await show_main_menu(update)


async def handle_webapp_auth(update: Update, arg: str):
    return_url = unquote(arg.split("_", 2)[-1]) if "_" in arg else WEB_APP_URL
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=return_url))],
    ]
    await update.message.reply_text(
        "Для авторизации в магазине поделитесь номером телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_complete_profile(update: Update):
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("✏️ Ввести имя")],
    ]
    await update.message.reply_text(
        "Пожалуйста, дополните ваш профиль:\n\n"
        "1. Нажмите «Поделиться номером»\n"
        "2. Или отправьте своё имя текстом",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    data = {
        "id": user.id,
        "first_name": user.first_name or contact.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": contact.phone_number,
        "auth_date": update.message.date.timestamp()
    }
    try:
        response = requests.post(API_URL, json=data)
        if response.ok:
            keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
            await update.message.reply_text(
                f"✅ Ваш номер {contact.phone_number} сохранён!",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await update.message.reply_text("⚠️ Не удалось сохранить данные.")
    except Exception as e:
        logger.error(f"Ошибка сохранения контакта: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text and not text.startswith("/"):
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
            response = requests.post(API_URL, json=data)
            if response.ok:
                keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
                await update.message.reply_text(
                    f"✅ Имя «{text}» сохранено!",
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                )
            else:
                await update.message.reply_text("⚠️ Не удалось сохранить имя.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении имени: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


async def show_main_menu(update: Update):
    keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы открыть магазин:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Ошибка при обработке:", exc_info=context.error)


# --- Запуск приложения через webhook ---
def run_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=WEBHOOK_URL
    )


if __name__ == "__main__":
    run_bot()
