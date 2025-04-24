from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import os
import requests

# Токен из переменных окружения или напрямую
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_TOKEN", "7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns")
SHOP_API_KEY = os.getenv("SHOP_API_KEY", "WWH15wOAGd0PwdBxGLc5nr2X0YGg0ALqXzbRUmpUoyqcpyXNs1RcyL1Hh1XUAKgbd4vmSKfSIrhA4lF4bdCais1F6WziIbcFBjmpzbCYst0Pz11Dyg0wvUrABdKPRlWz4Bd5ZNQD7wd8tNcJALBWQKmCi1kLcUtITtJaJLvAK2zb6bAs4bcxs6cWckd7LQdidT52hLU0xhZm3HXoSa3IrILHba0rSTwnqyCTe7DaPVlbssCUiSmUnJhHbtEMYySG")

# Асинхронная функция для команды /start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Адреса магазинов", callback_data="addresses")],
        [InlineKeyboardButton("Каталог товаров", callback_data="catalog")],
        [InlineKeyboardButton("Оставить отзыв", callback_data="review")],
        [InlineKeyboardButton("Контакты", callback_data="contacts")],
        [InlineKeyboardButton("Вакансии", callback_data="jobs")],
        [InlineKeyboardButton("Акции", callback_data="promotions")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Добро пожаловать! Выберите нужный раздел:', reply_markup=reply_markup)

# Обработчик нажатий на кнопки
async def button(update: Update, context):
    query = update.callback_query
    choice = query.data

    if choice == "addresses":
        await query.answer()
        await query.edit_message_text("Выберите область:")
        # Логика для отображения списка областей
    elif choice == "catalog":
        await query.answer()
        await query.edit_message_text("Выберите категорию товаров:")
        # Логика для отображения категорий товаров
    elif choice == "review":
        await query.answer()
        await query.edit_message_text("Оставьте отзыв:")
        # Логика для формы отзыва
    elif choice == "contacts":
        await query.answer()
        await query.edit_message_text("Контактная информация:")
        # Логика для отображения контактов
    elif choice == "jobs":
        await query.answer()
        await query.edit_message_text("Вакансии:")
        # Логика для отображения вакансий
    elif choice == "promotions":
        await query.answer()
        await query.edit_message_text("Акции и новости:")
        # Логика для отображения акций

# Получение информации о магазинах через API
def get_shop_info():
    response = requests.get('https://api.shop.com/addresses', headers={'Authorization': f'Bearer {SHOP_API_KEY}'})
    return response.json()

# Получение каталога товаров через API
def get_product_catalog():
    response = requests.get('https://api.shop.com/products', headers={'Authorization': f'Bearer {SHOP_API_KEY}'})
    return response.json()

# Основная функция для запуска бота
def main():
    # Создание Application с передачей токена
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Добавление обработчиков команд
    start_handler = CommandHandler("start", start)
    button_handler = CallbackQueryHandler(button)  # Обработчик кнопок
    application.add_handler(start_handler)
    application.add_handler(button_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
