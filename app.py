from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import config

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

if __name__ == '__main__':
    main()
