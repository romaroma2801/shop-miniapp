from flask import Flask, jsonify, request, render_template
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json
import logging
import threading
import requests
from urllib.parse import unquote

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

# Инициализация данных
USER_DATA_PATH = os.path.join(os.getcwd(), 'users.json')
if not os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, 'w') as f:
        json.dump([], f)

# Загрузка данных магазинов
with open('store_full.json', 'r', encoding='utf-8') as file:
    STORE_DATA = json.load(file)

# ==================== Flask Routes ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/regions', methods=['GET'])
def get_regions():
    regions = list(STORE_DATA.keys())
    return jsonify(regions)

@app.route('/api/cities/<region>', methods=['GET'])
def get_cities(region):
    cities = list(STORE_DATA.get(region, {}).keys())
    return jsonify(cities)

@app.route('/api/stores/<region>/<city>', methods=['GET'])
def get_stores(region, city):
    stores = STORE_DATA.get(region, {}).get(city, [])
    return jsonify(stores)

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    try:
        response = requests.get('https://nekuri.by/api/news-feed.php')
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        new_data = request.json
        if not new_data or 'id' not in new_data:
            return jsonify({"status": "error", "message": "Invalid data"}), 400
        
        with open(USER_DATA_PATH, 'r+') as f:
            users = json.load(f)
            user_index = next((i for i, u in enumerate(users) if u.get('id') == new_data['id']), None)
            
            if user_index is not None:
                # Обновляем существующего пользователя
                for key, value in new_data.items():
                    if value and value != 'не указан':
                        users[user_index][key] = value
            else:
                # Добавляем нового пользователя
                users.append({
                    "id": new_data['id'],
                    "first_name": new_data.get('first_name', 'не указано'),
                    "last_name": new_data.get('last_name', ''),
                    "username": new_data.get('username', 'не указан'),
                    "phone": new_data.get('phone', 'не указан')
                })
            
            f.seek(0)
            json.dump(users, f, indent=2)
            f.truncate()
        
        return jsonify({
            "status": "success",
            "user": next((u for u in users if u['id'] == new_data['id']), new_data)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== Telegram Bot Handlers ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            await show_main_menu(update)
            return
        
        if args[0].startswith('webapp_auth'):
            await handle_webapp_auth(update, args[0])
        elif args[0].startswith('request_phone'):
            await request_phone_number(update, args[0])
        elif args[0].startswith('complete_profile'):
            await handle_complete_profile(update)
        else:
            await show_main_menu(update)
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def handle_webapp_auth(update: Update, arg: str):
    return_url = unquote(arg.split('_', 2)[-1]) if '_' in arg else WEB_APP_URL
    
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=return_url))]
    ]
    await update.message.reply_text(
        "Для авторизации поделитесь номером телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_complete_profile(update: Update):
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("✏️ Ввести имя")]
    ]
    await update.message.reply_text(
        "Пожалуйста, дополните ваш профиль:\n\n"
        "1. Нажмите «Поделиться номером» для отправки телефона\n"
        "2. Или напишите свое имя в ответном сообщении",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def request_phone_number(update: Update, arg: str):
    return_url = unquote(arg.split('_', 2)[-1]) if '_' in arg else WEB_APP_URL
    
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Вернуться в магазин", web_app=WebAppInfo(url=return_url))]
    ]
    await update.message.reply_text(
        "Для полного доступа к магазину нам нужен ваш номер телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    
    user_data = {
        "id": user.id,
        "first_name": user.first_name or contact.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": contact.phone_number,
        "auth_date": update.message.date.timestamp()
    }
    
    try:
        response = requests.post(f"{WEB_APP_URL}/api/save-user", json=user_data)
        if response.status_code == 200:
            keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
            await update.message.reply_text(
                f"✅ Ваш номер {contact.phone_number} сохранён!\n"
                "Теперь вы можете вернуться в приложение:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await update.message.reply_text("⚠️ Ошибка при сохранении данных. Попробуйте позже.")
    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка соединения с сервером.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and not update.message.text.startswith('/'):
        user = update.effective_user
        
        user_data = {
            "id": user.id,
            "first_name": update.message.text,
            "last_name": user.last_name or "",
            "username": user.username or "не указан",
            "phone": "не указан",
            "auth_date": update.message.date.timestamp()
        }
        
        try:
            response = requests.post(f"{WEB_APP_URL}/api/save-user", json=user_data)
            if response.status_code == 200:
                keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
                await update.message.reply_text(
                    f"✅ Ваше имя «{update.message.text}» сохранено!\n"
                    "Теперь вы можете вернуться в приложение:",
                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                )
            else:
                await update.message.reply_text("⚠️ Ошибка при сохранении данных. Попробуйте позже.")
        except Exception as e:
            await update.message.reply_text("⚠️ Ошибка соединения с сервером.")

async def show_main_menu(update: Update):
    keyboard = [[KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text(
        "Добро пожаловать! Используйте кнопку ниже для открытия магазина:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update.message:
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

def run_bot():
    """Запуск Telegram бота в отдельном потоке"""
    try:
        logger.info(f"Initializing bot with token: {TELEGRAM_TOKEN[:5]}...{TELEGRAM_TOKEN[-5:]}")
        
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Явно регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        logger.info("Bot handlers registered:")
        for handler in application.handlers[0]:
            logger.info(f"- {handler.callback.__name__}")
        
        logger.info("Starting bot polling...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        raise

# ==================== Запуск приложения ====================

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask приложение
    logger.info(f"Starting Flask app on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)
