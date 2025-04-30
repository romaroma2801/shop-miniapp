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
    
    # Обработка deep links
    if args[0].startswith('webapp_auth_'):
        # Пользователь пришел из WebApp для авторизации
        return_url = unquote(args[0][12:])
        await handle_webapp_auth(update, return_url)
    elif args[0].startswith('request_phone_'):
        # Запрос номера телефона
        return_url = unquote(args[0][14:])
        await request_phone_number(update, return_url)
    else:
        await show_main_menu(update)

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
    
    # Подготавливаем данные для отправки
    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": contact.phone_number,
        "auth_date": update.message.date.timestamp()
    }
    
    # Отправляем данные на сервер
    try:
        response = requests.post(API_URL, json=user_data)
        if response.status_code == 200:
            # Формируем кнопку для возврата в WebApp
            keyboard = [
                [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=WEB_APP_URL))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "✅ Вы успешно авторизованы!\n"
                f"Ваш номер: {contact.phone_number}\n"
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
