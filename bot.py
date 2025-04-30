from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://shop-miniapp.onrender.com")

async def start(update: Update, context):
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Нажмите кнопку, чтобы поделиться номером:",
        reply_markup=keyboard
    )

async def handle_contact(update: Update, context):
    phone = update.message.contact.phone_number
    await update.message.reply_text(f"Спасибо! Ваш номер {phone} сохранён.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    app.run_polling()

if __name__ == '__main__':
    main()
