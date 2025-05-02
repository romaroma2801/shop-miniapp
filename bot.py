from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
import signal

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP")

application = None  # Глобальная переменная для обработчика сигналов

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с inline кнопкой в сообщении"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Открыть приложение", url=WEB_APP_URL)]
    ])
    
    await update.message.reply_text(
        "Добро пожаловать в наш магазин!\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений - просто перенаправляет на старт"""
    await start(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def stop_bot(signum, frame):
    """Обработчик сигнала для корректного завершения"""
    logger.info("Stopping bot gracefully...")
    if application:
        application.stop()

def main():
    global application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Обработка сигналов
    signal.signal(signal.SIGTERM, stop_bot)
    signal.signal(signal.SIGINT, stop_bot)
    
    logger.info("Starting bot polling...")
    application.run_polling(
        drop_pending_updates=True,
        close_loop=False,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == '__main__':
    main()
