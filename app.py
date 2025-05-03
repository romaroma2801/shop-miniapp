import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# --- Flask App Setup ---
app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# --- Load Store Data ---
try:
    with open('store_full.json', 'r', encoding='utf-8') as file:
        STORE_DATA = json.load(file)
except Exception as e:
    logging.error(f"Failed to load store data: {e}")
    STORE_DATA = {}
    logging.error(f"get_user error: {e}")
    return jsonify({"error": str(e)}), 500

# --- Google Sheets ---
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
    client = gspread.authorize(creds)
    return client.open("USERS").sheet1

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-user')
def get_user():
    username = request.args.get('username')  # Получаем username из запроса
    if not username:
        return jsonify({'error': 'No username provided'}), 400

    try:
        # Авторизация в Google Sheets
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            {
                "type": "service_account",
                "project_id": os.getenv("GSHEETS_PROJECT_ID"),
                "private_key_id": os.getenv("GSHEETS_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GSHEETS_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("GSHEETS_CLIENT_EMAIL"),
                "client_id": os.getenv("GSHEETS_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("GSHEETS_CLIENT_CERT_URL"),
            },
            ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )

        client = gspread.authorize(credentials)
        sheet = client.open_by_url(os.getenv("USERS")).sheet1
        users = sheet.get_all_records()

        for user in users:
            if user["Username"] == username:
                return jsonify(user)

        return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        print("Auth error:", e)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.json
        sheet = get_sheet()
        records = sheet.get_all_records()
        user_index = next((i for i, u in enumerate(records) if u['Username'] == data['username']), None)

        if user_index is not None:
            row = user_index + 2
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

@app.route('/api/regions')
def get_regions():
    return jsonify(list(STORE_DATA.keys()))

@app.route('/api/cities/<region>')
def get_cities(region):
    return jsonify(list(STORE_DATA.get(region, {}).keys()))

@app.route('/api/stores/<region>/<city>')
def get_stores(region, city):
    return jsonify(STORE_DATA.get(region, {}).get(city, []))

@app.route('/api/promotions')
def get_promotions():
    try:
        response = requests.get('https://nekuri.by/api/news-feed.php')
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Напишите название города, чтобы найти магазин.")

async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    found = False
    for region, cities in STORE_DATA.items():
        if city in cities:
            stores = cities[city]
            buttons = [
                [InlineKeyboardButton(store["address"], url=store.get("map_link", "#"))]
                for store in stores
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"Магазины в городе {city}:", reply_markup=reply_markup)
            found = True
            break
    if not found:
        await update.message.reply_text("Город не найден. Попробуйте снова.")

# --- Telegram Setup ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))

# --- Webhook Route for Telegram ---
@app.route('/webhook', methods=['POST'])
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return 'ok'

# --- Launch Flask App ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=PORT)
