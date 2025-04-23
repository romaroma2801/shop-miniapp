import asyncio
from telegram import Update, ext
from flask import Flask, render_template
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import requests
import config

# Инициализация Flask-приложения
app = Flask(__name__)

# Инициализация бота
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf'Привет {user.mention_html()}! Добро пожаловать в наш магазин.',
        reply_markup=ext.ReplyKeyboardMarkup([['Запустить приложение']], one_time_keyboard=True),
    )

async def show_main_menu(update: Update, context: CallbackContext):
    reply_markup = ext.ReplyKeyboardMarkup([
        ['Адреса магазинов', 'Каталог товаров'],
        ['Оставить отзыв', 'Контакты'],
        ['Вакансии', 'Акции']
    ], resize_keyboard=True)

    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

async def handle_catalog(update: Update, context: CallbackContext):
    # Здесь будет логика для отображения категорий товаров
    pass

async def handle_address(update: Update, context: CallbackContext):
    # Здесь будет логика для отображения адресов магазинов
    pass

async def handle_review(update: Update, context: CallbackContext):
    # Здесь будет логика для обработки отзывов
    pass

# Инициализация Application и диспетчера
async def main():
    # Создание объекта Application с токеном
    application = Application.builder().token(config.TELEGRAM_API_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_main_menu))

    # Запуск бота
    await application.run_polling()

# Запуск Flask-приложения
@app.route("/")
def index():
    return render_template("index.html")

# Для асинхронного запуска Flask и Telegram-бота в одном цикле событий
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Запуск Flask-приложения в фоновом потоке
    loop.create_task(main())

    # Запуск Flask-сервера
    import os

# Получаем порт из переменной окружения, установленной на Render
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
  # use_reloader=False для предотвращения повторного запуска

