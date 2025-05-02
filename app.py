from flask import Flask, jsonify, request, render_template
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json
import logging
import asyncio
from threading import Thread
import requests

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
PORT = int(os.environ.get('PORT', 5000))

# Инициализация Flask
app = Flask(__name__)

# ==================== Flask Routes ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    try:
        response = requests.get('https://nekuri.by/api/news-feed.php')
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Telegram Bot Handlers ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text(
        "Добро пожаловать в наш магазин!\n\nНажмите кнопку ниже, чтобы открыть интернет-магазин:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text(
        "Используйте кнопку ниже, чтобы открыть магазин:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

async def run_bot():
    """Запуск Telegram бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("Starting bot polling...")
    await application.run_polling()

def run_flask():
    """Запуск Flask приложения"""
    logger.info(f"Starting Flask app on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)

async def main():
    """Основная функция для запуска всего приложения"""
    # Создаем и запускаем задачи
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота в основном потоке
    await run_bot()

if __name__ == '__main__':
    asyncio.run(main())
