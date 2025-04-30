from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://shop-miniapp.onrender.com")

async def start(update: Update, context):
    # Кнопка для авторизации
    auth_button = KeyboardButton(
        "🔑 Авторизоваться", 
        web_app=WebAppInfo(url=f"{WEB_APP_URL}/auth")
    )
    
    # Кнопка для отправки номера
    phone_button = KeyboardButton(
        "📱 Отправить номер", 
        request_contact=True
    )
    
    reply_markup = ReplyKeyboardMarkup(
        [[auth_button], [phone_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await update.message.reply_text(
        "Выберите способ авторизации:",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context):
    contact = update.message.contact
    await update.message.reply_text(
        f"Спасибо, {contact.first_name}! Номер сохранён.",
        reply_markup=ReplyKeyboardRemove()
    )
    # Здесь можно сохранить номер в базу

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    setup_handlers(app)
    app.run_polling()
