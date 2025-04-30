from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os
import requests
import json
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv()

# === Flask ===
app = Flask(__name__)
CORS(app, origins=[os.getenv("TELEGRAM_WEB_APP_URL")])

# === Данные магазинов ===
with open('store_full.json', 'r', encoding='utf-8') as f:
    STORE_DATA = json.load(f)

USER_DATA_PATH = os.path.join(os.getcwd(), 'users.json')
if not os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, 'w') as f:
        json.dump([], f)

@app.before_request
def log_request():
    print(f"{request.method} {request.url}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/regions')
def get_regions():
    return jsonify(list(STORE_DATA.keys()))

@app.route('/api/cities/<region>')
def get_cities(region):
    return jsonify(list(STORE_DATA.get(region, {}).keys()))

@app.route('/api/stores/<region>/<city>')
def get_stores(region, city):
    return jsonify(STORE_DATA.get(region, {}).get(city, []))

@app.route('/api/save-user', methods=["POST"])
def save_user():
    try:
        data = request.json
        if not data or 'id' not in data:
            return jsonify({"status": "error", "message": "Invalid data"}), 400

        users = []
        if os.path.exists(USER_DATA_PATH):
            with open(USER_DATA_PATH, 'r') as f:
                users = json.load(f)

        user_index = next((i for i, u in enumerate(users) if u.get('id') == data['id']), None)

        if user_index is not None:
            for key, value in data.items():
                if value and value != 'не указан':
                    users[user_index][key] = value
        else:
            users.append({
                "id": data['id'],
                "first_name": data.get('first_name', 'не указано'),
                "last_name": data.get('last_name', ''),
                "username": data.get('username', 'не указан'),
                "phone": data.get('phone', 'не указан')
            })

        with open(USER_DATA_PATH, 'w') as f:
            json.dump(users, f, indent=2)

        return jsonify({"status": "success", "user": users[user_index if user_index is not None else -1]})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# === Telegram Bot ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        param = args[0]
        if param.startswith("webapp_auth"):
            return await handle_webapp_auth(update, param)
        elif param.startswith("complete_profile"):
            return await handle_complete_profile(update)
    await show_main_menu(update)

async def handle_webapp_auth(update: Update, arg: str):
    return_url = unquote(arg.split("_", 2)[-1]) if "_" in arg else WEB_APP_URL
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("🛍️ Открыть магазин", web_app=WebAppInfo(url=return_url))]
    ]
    await update.message.reply_text(
        "Для авторизации в магазине поделитесь номером:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_complete_profile(update: Update):
    keyboard = [
        [KeyboardButton("📱 Поделиться номером", request_contact=True)],
        [KeyboardButton("✏️ Ввести имя")]
    ]
    await update.message.reply_text(
        "Пожалуйста, дополните ваш профиль:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    data = {
        "id": user.id,
        "first_name": user.first_name or contact.first_name,
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": contact.phone_number,
        "auth_date": update.message.date.timestamp()
    }
    try:
        r = requests.post(f"{WEB_APP_URL}/api/save-user", json=data)
        if r.ok:
            await update.message.reply_text("✅ Ваш номер сохранён!")
        else:
            await update.message.reply_text("⚠️ Не удалось сохранить данные.")
    except Exception as e:
        await update.message.reply_text("Произошла ошибка.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    data = {
        "id": user.id,
        "first_name": text,
        "last_name": user.last_name or "",
        "username": user.username or "не указан",
        "phone": "не указан",
        "auth_date": update.message.date.timestamp()
    }
    try:
        r = requests.post(f"{WEB_APP_URL}/api/save-user", json=data)
        if r.ok:
            await update.message.reply_text(f"✅ Имя {text} сохранено!")
        else:
            await update.message.reply_text("⚠️ Не удалось сохранить имя.")
    except Exception as e:
        await update.message.reply_text("Произошла ошибка.")

async def show_main_menu(update: Update):
    await update.message.reply_text("Добро пожаловать! Воспользуйтесь кнопками WebApp.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Webhook endpoint ===
@app.route('/webhook', methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# === Запуск ===
if __name__ == '__main__':
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=WEBHOOK_URL
    )
