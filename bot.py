from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from telegram.ext import Application
from telegram.ext.webhook import WebhookHandler
import requests
import logging
from urllib.parse import unquote

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
API_URL = os.getenv("API_URL", "http://localhost:5000/api/save-user")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с параметрами"""
    try:
        logger.info(f"Получена команда start от пользователя: {update.effective_user.id}")
        logger.info(f"Аргументы команды: {context.args}")
        
        args = context.args
        if not args:
            logger.info("Обычный запуск без параметров")
            await show_main_menu(update)
            return
        
        # Обработка различных вариантов команды start
        if args[0].startswith('webapp_auth'):
            logger.info("Запрос авторизации из WebApp")
            await handle_webapp_auth(update, args[0])
        elif args[0].startswith('request_phone'):
            logger.info("Запрос номера телефона")
            await request_phone_number(update, args[0])
        elif args[0].startswith('complete_profile'):
            logger.info("Запрос дополнения профиля")
            await handle_complete_profile(update)
        else:
            logger.info("Неизвестные параметры, показ главного меню")
            await show_main_menu(update)
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике start: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_webapp_auth(update: Update, arg: str):
    """Обработка авторизации из WebApp"""
    try:
        return_url = unquote(arg.split('_', 2)[-1]) if '_' in arg else WEB_APP_URL
        
        keyboard = [
            [KeyboardButton("📱 Поделиться номером", request_contact=True)],
            [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=return_url))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Для авторизации в магазине поделитесь номером телефона:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_webapp_auth: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_complete_profile(update: Update):
    """Обработка запроса на дополнение профиля"""
    try:
        keyboard = [
            [KeyboardButton("📱 Поделиться номером", request_contact=True)],
            [KeyboardButton("✏️ Ввести имя")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Пожалуйста, дополните ваш профиль:\n\n"
            "1. Нажмите «Поделиться номером» для отправки телефона\n"
            "2. Или напишите свое имя в ответном сообщении",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_complete_profile: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def request_phone_number(update: Update, arg: str):
    """Запрос номера телефона"""
    try:
        return_url = unquote(arg.split('_', 2)[-1]) if '_' in arg else WEB_APP_URL
        
        keyboard = [
            [KeyboardButton("📱 Поделиться номером", request_contact=True)],
            [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=return_url))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Для полного доступа к магазину нам нужен ваш номер телефона:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в request_phone_number: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка полученного контакта"""
    try:
        contact = update.message.contact
        user = update.effective_user
        logger.info(f"Получен контакт от пользователя {user.id}")
        
        user_data = {
            "id": user.id,
            "first_name": user.first_name or contact.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "не указан",
            "phone": contact.phone_number,
            "auth_date": update.message.date.timestamp()
        }
        
        response = requests.post(API_URL, json=user_data)
        if response.status_code == 200:
            keyboard = [
                [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"✅ Ваш номер {contact.phone_number} сохранён!\n"
                "Теперь вы можете вернуться в приложение:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("⚠️ Ошибка при сохранении данных. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в handle_contact: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (для имени)"""
    try:
        if update.message.text and not update.message.text.startswith('/'):
            user = update.effective_user
            logger.info(f"Получено имя от пользователя {user.id}")
            
            user_data = {
                "id": user.id,
                "first_name": update.message.text,
                "last_name": user.last_name or "",
                "username": user.username or "не указан",
                "phone": "не указан",
                "auth_date": update.message.date.timestamp()
            }
            
            response = requests.post(API_URL, json=user_data)
            if response.status_code == 200:
                keyboard = [
                    [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                
                await update.message.reply_text(
                    f"✅ Ваше имя «{update.message.text}» сохранено!\n"
                    "Теперь вы можете вернуться в приложение:",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("⚠️ Ошибка при сохранении данных. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def show_main_menu(update: Update):
    """Показ главного меню"""
    try:
        keyboard = [
            [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Добро пожаловать! Используйте кнопку ниже для открытия магазина:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в show_main_menu: {str(e)}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке сообщения: {context.error}")
    if update.message:
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

WEBHOOK_URL = os.getenv("https://shop-miniapp.onrender.com")  # Укажи свой домен, например https://your-app.onrender.com

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Важно: запускаем webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=WEBHOOK_URL + "/webhook"
    )
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")

if __name__ == '__main__':
    main()
