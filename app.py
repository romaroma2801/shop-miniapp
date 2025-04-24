import os
from flask import Flask, render_template
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import config

# Инициализация Flask-приложения
app = Flask(__name__)

# Главная страница веб-приложения
@app.route("/")
def index():
    return render_template("index.html")

# Функция для команды /start в Telegram
def start(update: Update, context: CallbackContext) -> None:
    # Создание Inline кнопки для открытия веб-приложения
    keyboard = [
        [InlineKeyboardButton("Открыть веб-приложение", web_app={'url': 'https://shop-miniapp.onrender.com'})]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Привет! Нажми на кнопку для открытия веб-приложения.",
        reply_markup=reply_markup
    )

# Функция для запуска Telegram-бота
def main():
    # Создание объекта Application с токеном
    updater = Updater(config.TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Регистрируем обработчик для команды /start
    dispatcher.add_handler(CommandHandler('start', start))
    
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    # Получаем порт из переменной окружения (для Render)
    port = int(os.environ.get("PORT", 5000))
    
    # Запуск Flask-приложения
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
    
    # Запуск Telegram-бота в фоновом режиме
    main()
