from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
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
    logger.info(f"Получена команда start с аргументами: {context.args}")
    
    # Разбираем аргументы команды
    args = context.args
    if not args:
        await show_main_menu(update)
        return
    
    if args[0] == 'complete_profile':
        await handle_complete_profile(update)
    else:
        await show_main_menu(update)

async def handle_complete_profile(update: Update):
    """Обработка запроса на дополнение профиля"""
    user = update.effective_user
    logger.info(f"Запрос на дополнение профиля от пользователя {user.id}")
    
    # Создаем клавиатуру с кнопкой "Поделиться номером"
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("✏️ Ввести имя", request_location=False)]  # Можно заменить на запрос имени
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Пожалуйста, дополните ваш профиль:\n\n"
        "1. Нажмите «Поделиться номером» для отправки телефона\n"
        "2. Или напишите свое имя в ответном сообщении",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка полученного контакта"""
    contact = update.message.contact
    user = update.effective_user
    logger.info(f"Получен контакт от пользователя {user.id}")
    
    # Здесь можно отправить данные на ваш сервер
    await update.message.reply_text(
        f"Спасибо! Ваш номер {contact.phone_number} сохранён.\n"
        "Теперь вы можете вернуться в приложение.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]],
            resize_keyboard=True
        )
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (для имени)"""
    if update.message.text and not update.message.text.startswith('/'):
        user = update.effective_user
        logger.info(f"Получено имя от пользователя {user.id}: {update.message.text}")
        
        # Здесь можно отправить имя на ваш сервер
        await update.message.reply_text(
            f"Спасибо! Ваше имя «{update.message.text}» сохранено.\n"
            "Теперь вы можете вернуться в приложение.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]],
                resize_keyboard=True
            )
        )

async def show_main_menu(update: Update):
    """Показ главного меню"""
    await update.message.reply_text(
        "Добро пожаловать! Используйте кнопки ниже:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]],
            resize_keyboard=True
        )
    )

def main():
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
