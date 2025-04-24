from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import config

# Функция для команды /start в Telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    # Создание кнопки для открытия веб-приложения
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", url="https://t.me/Shop_NEKURIBY_bot/Shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Добро пожаловать в наш бот! Нажмите кнопку ниже, чтобы открыть приложение:', reply_markup=reply_markup)


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
