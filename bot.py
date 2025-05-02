from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
import signal
import sys
import psutil

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Добро пожаловать в наш магазин!\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Открыть приложение", url=WEB_APP_URL)]
        ])
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений"""
    await start(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
def stop_bot(signum, frame):
    logger.info("Bot is shutting down gracefully...")
    sys.exit(0)

def main():
    # Создаем приложение
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
        stop_signals=None  # Важно!
    )

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        sys.exit(1)
