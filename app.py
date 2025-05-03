from flask import Flask, request, jsonify, render_template
import os
import json
import logging
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

app = Flask(__name__)

# --- Настройки
PORT = int(os.environ.get('PORT', 5000))
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # https://your-app.onrender.com
WEB_APP = os.getenv('WEB_APP', 'https://t.me/Shop_NEKURIBY_bot/Shop')

bot = Bot(token=TELEGRAM_TOKEN)

# --- Dispatcher Telegram
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# --- Загрузка данных магазинов
try:
    with open('store_full.json', 'r', encoding='utf-8') as file:
        STORE_DATA = json.load(file)
except Exception as e:
    STORE_DATA = {}
    logging.error(f"Store data load error: {e}")

# --- Google Sheets авторизация
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": os.getenv("GSHEETS_PROJECT_ID"),
        "private_key_id": os.getenv("GSHEETS_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GSHEETS_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GSHEETS_CLIENT_EMAIL"),
        "client_id": os.getenv("GSHEETS_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GSHEETS_CLIENT_CERT_URL")
    }, scope)
    return gspread.authorize(creds).open("USERS").sheet1

# --- Telegram handlers
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Открыть приложение", url=WEB_APP)]]
    update.message.reply_text("Добро пожаловать!", reply_markup=InlineKeyboardMarkup(keyboard))

dispatcher.add_handler(CommandHandler("start", start))

# --- Webhook endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# --- Webhook set on startup
@app.before_first_request
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    bot.set_webhook(url=webhook_url)

# --- Статические страницы и API
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-user', methods=['GET'])
def get_user():
    username = request.args.get('username')
    try:
        sheet = get_sheet()
        user = next((u for u in sheet.get_all_records() if u['Username'] == username), None)
        return jsonify({"exists": bool(user), "user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.json
        sheet = get_sheet()
        records = sheet.get_all_records()
        idx = next((i for i, u in enumerate(records) if u['Username'] == data['username']), None)
        if idx is not None:
            row = idx + 2
            if data.get('name'):
                sheet.update_cell(row, 2, data['name'])
            if data.get('phone'):
                sheet.update_cell(row, 3, data['phone'])
        else:
            sheet.append_row([
                data['username'],
                data.get('name', ''),
                data.get('phone', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/regions', methods=['GET'])
def get_regions():
    return jsonify(list(STORE_DATA.keys()))

@app.route('/api/cities/<region>', methods=['GET'])
def get_cities(region):
    return jsonify(list(STORE_DATA.get(region, {}).keys()))

@app.route('/api/stores/<region>/<city>', methods=['GET'])
def get_stores(region, city):
    return jsonify(STORE_DATA.get(region, {}).get(city, []))

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    try:
        res = requests.get('https://nekuri.by/api/news-feed.php')
        res.raise_for_status()
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Запуск сервера (не нужен на Render, но полезен локально)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=PORT)
