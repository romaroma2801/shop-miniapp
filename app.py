from telegram import Update, ext
from flask import Flask, render_template
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import requests
import config

# Инициализация Flask-приложения
app = Flask(__name__)

# Инициализация бота
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf'Привет {user.mention_html()}! Добро пожаловать в наш магазин.',
        reply_markup=ext.ReplyKeyboardMarkup([['Запустить приложение']], one_time_keyboard=True),
    )

def show_main_menu(update: Update, context: CallbackContext):
    reply_markup = ext.ReplyKeyboardMarkup([
        ['Адреса магазинов', 'Каталог товаров'],
        ['Оставить отзыв', 'Контакты'],
        ['Вакансии', 'Акции']
    ], resize_keyboard=True)

    update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

def handle_catalog(update: Update, context: CallbackContext):
    # Здесь будет логика для отображения категорий товаров
    pass

def handle_address(update: Update, context: CallbackContext):
    # Здесь будет логика для отображения адресов магазинов
    pass

def handle_review(update: Update, context: CallbackContext):
    # Здесь будет логика для обработки отзывов
    pass

def main():
    updater = Updater(config.TELEGRAM_API_TOKEN)
    dispatcher = updater.dispatcher

    # Регистрируем команды
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(ext.Filters.text & ~ext.Filters.command, show_main_menu))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

# Запуск Flask-приложения
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
