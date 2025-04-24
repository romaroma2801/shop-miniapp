from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
import os

# Токен из переменных окружения или напрямую
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_TOKEN", "7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns")

# Асинхронная функция для команды /start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", url="https://t.me/Shop_NEKURIBY_bot/Shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Добро пожаловать в наш бот! Нажмите кнопку ниже, чтобы открыть приложение:', reply_markup=reply_markup)

# Основная функция для запуска бота
def main():
    # Создание Application с передачей токена
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Добавление обработчиков команд
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
