from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
from urllib.parse import unquote

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
API_URL = os.getenv("API_URL", "http://localhost:5000/api/save-user")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await show_main_menu(update)
        return
    
    if args[0].startswith('complete_profile_'):
        return_url = unquote(args[0][16:])
        await handle_complete_profile(update, return_url)
    # ... остальные обработчики

async def handle_complete_profile(update: Update, return_url: str):
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=return_url or WEB_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Пожалуйста, предоставьте недостающие данные:\n"
        "1. Нажмите 'Поделиться номером' для отправки телефона\n"
        "2. Или просто напишите свое имя",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обработка текстового сообщения с именем
    if update.message.text and not update.message.text.startswith('/'):
        user = update.effective_user
        user_data = {
            "id": user.id,
            "first_name": update.message.text,  # Используем текст сообщения как имя
            "last_name": user.last_name or "",
            "username": user.username or "не указан",
            "phone": "не указан"
        }
        
        await save_user_data(update, user_data)

async def handle_webapp_auth(update: Update, return_url: str):
    user = update.effective_user
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=return_url or WEB_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        "Для авторизации в магазине поделитесь номером телефона:",
        reply_markup=reply_markup
    )

async def request_phone_number(update: Update, return_url: str):
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=return_url or WEB_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Для полного доступа к магазину нам нужен ваш номер телефона:",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    
    user_data = {
        "id": user.id,
        "first_name": user.first_name or contact.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": contact.phone_number,
    }
    
    await save_user_data(update, user_data)

async def save_user_data(update: Update, user_data: dict):
    try:
        response = requests.post(API_URL, json=user_data)
        if response.status_code == 200:
            keyboard = [
                [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=WEB_APP_URL))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "✅ Ваши данные успешно сохранены!\n"
                f"Имя: {user_data['first_name']}\n"
                f"Телефон: {user_data.get('phone', 'не указан')}\n"
                "Теперь вы можете вернуться в магазин:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("⚠️ Ошибка при сохранении данных. Попробуйте позже.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка соединения: {str(e)}")

async def show_main_menu(update: Update):
    keyboard = [
        [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Добро пожаловать в магазин NEKURI!\n"
        "Нажмите кнопку ниже, чтобы открыть магазин:",
        reply_markup=reply_markup
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    app.run_polling()

if __name__ == '__main__':
    main()
