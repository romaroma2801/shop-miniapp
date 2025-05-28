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
    # Удалено ошибочное возвращение return вне функции

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
@app.route('/user')
def user_page():
    return render_template('user.html')
@app.route('/order')
def order_page():
    return render_template('order.html')
@app.route('/api/get-user')
def get_user():
    username = request.args.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'No username provided'}), 400

    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        
        # Ищем пользователя (без учета регистра)
        user = next((u for u in records if u.get('Username', '').lower() == username.lower()), None)
        
        if user:
            return jsonify({
                'status': 'success',
                'user': user,
                'exists': True
            })
        else:
            return jsonify({
                'status': 'success',
                'user': {
                    'Username': username,
                    'name': '',
                    'phone': ''
                },
                'exists': False
            })

    except Exception as e:
        logging.error(f"Error in get_user: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.json
        if not data.get('username'):
            return jsonify({'status': 'error', 'message': 'Username is required'}), 400

        sheet = get_sheet()
        records = sheet.get_all_records()
        
        # Проверяем существование пользователя
        user_index = next((i for i, u in enumerate(records) if u.get('Username', '').lower() == data['username'].lower()), None)
        
        if user_index is not None:
            # Обновляем существующего пользователя
            row = user_index + 2
            updates = []
            if data.get('name'):
                sheet.update_cell(row, 2, data['name'])
            if data.get('phone'):
                sheet.update_cell(row, 3, data['phone'])
            message = "User updated"
        else:
            # Добавляем нового пользователя
            sheet.append_row([
                data['username'],
                data.get('name', ''),
                data.get('phone', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            message = "User created"
        
        return jsonify({"status": "success", "message": message})
    
    except Exception as e:
        logging.error(f"Error in save_user: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/catalog')
def catalog_page():
    return render_template('catalog.html')
@app.route('/api/catalog')
def get_catalog():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://nekuri.by/parser/output/catalog.json', headers=headers)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            # Преобразуем список в словарь по id
            data = {str(item['id']): item for item in data if isinstance(item, dict) and 'id' in item}

        if not isinstance(data, dict):
            raise ValueError("Каталог имеет неподдерживаемую структуру")

        return jsonify(data)

    except Exception as e:
        import logging
        logging.error(f"Ошибка при загрузке каталога: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
        response = requests.get('https://nekuri.by/api/news-feed.json')
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        if not data.get('username'):
            # Получаем username из данных Telegram, если не передан
            if Telegram.WebApp.initDataUnsafe and Telegram.WebApp.initDataUnsafe.user:
                data['username'] = Telegram.WebApp.initDataUnsafe.user.username or f"id{Telegram.WebApp.initDataUnsafe.user.id}"
            else:
                return jsonify({'status': 'error', 'message': 'Username is required'}), 400

        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        
        # Проверяем, не был ли уже добавлен этот заказ
        existing_order = next((o for o in records if 
                             o.get('username') == data['username'] and 
                             abs((
                                datetime.strptime(o['order_date'], "%Y-%m-%d %H:%M:%S") -
                                (datetime.utcnow() + timedelta(hours=3))
                            ).total_seconds()) < 60
                        ), None)
        if existing_order:
            return jsonify({"status": "error", "message": "Order already exists"}), 400
            
        last_order_id = records[-1]['order_id'] if records else 0
        order_id = last_order_id + 1
        
        order_date = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        items_str = json.dumps(data['items'], ensure_ascii=False)
        
        # Добавляем заказ только один раз
        sheet.append_row([
            order_id,
            data['username'],
            order_date,
            items_str,
            data['total'],
            data['discount'],
            data['delivery'],
            data['final_total'],
            'в обработке',
            data.get('customer_name', ''),
            data.get('city', ''),
            data.get('postcode', ''),
            data.get('address', ''),
            data.get('phone', '')
        ])
        
        send_order_notification(order_id, data)
        return jsonify({"status": "success", "order_id": order_id})
    
    except Exception as e:
        logging.error(f"Error in create_order: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def get_orders_sheet():
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
    return client.open("ORDERS").sheet1

def send_order_notification(order_id, order_data):
    try:
        message = f"🛒 <b>Новый заказ №{order_id}</b>\n"
        message += f"📅 Дата: {(datetime.utcnow() + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M:%S')}\n"
        message += f"👤 Пользователь: @{order_data['username']}\n\n"
        
        message += "🛍️ <b>Товары:</b>\n"
        for item in order_data['items']:
            message += f"- {item['title']}"
            if item.get('option'):
                message += f" ({item['option']})"
            message += f" × {item['quantity']} = {item['price'] * item['quantity']:.2f} BYN\n"
        
        message += "\n💰 <b>Суммы:</b>\n"
        message += f"Скидка 3%: -{order_data['discount']:.2f} BYN\n"
        message += f"Доставка: {order_data['delivery']:.2f} BYN\n"
        message += f"Итого: {order_data['final_total']:.2f} BYN\n\n"
        
        if order_data.get('customer_name'):
            message += f"👤 <b>Клиент:</b> {order_data['customer_name']}\n"
        if order_data.get('city'):
            message += f"🏙️ <b>Город:</b> {order_data['city']}\n"
        if order_data.get('postcode'):
            message += f"📮 <b>Индекс:</b> {order_data['postcode']}\n"
        if order_data.get('address'):
            message += f"🏠 <b>Адрес:</b> {order_data['address']}\n"
        if order_data.get('phone'):
            message += f"📱 <b>Телефон:</b> {order_data['phone']}\n"
        
        # Отправляем сообщение в Telegram (используем тот же чат, что и для отзывов)
        requests.post(
            'https://api.telegram.org/bot7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns/sendMessage',
            json={
                'chat_id': '568416622',
                'text': message,
                'parse_mode': 'HTML'
            }
        )
    except Exception as e:
        logging.error(f"Error sending Telegram notification: {str(e)}")
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
@app.route('/api/get-orders')
def get_orders():
    username = request.args.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'No username provided'}), 400

    try:
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        
        # Фильтруем заказы пользователя и сортируем по дате (новые сначала)
        user_orders = [
            order for order in records 
            if order.get('username', '').lower() == username.lower()
        ]
        user_orders.sort(key=lambda x: x['order_date'], reverse=True)
        
        return jsonify(user_orders)
    except Exception as e:
        logging.error(f"Error in get_orders: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-order/<int:order_id>')
def get_order(order_id):
    try:
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        
        order = next((o for o in records if o['order_id'] == order_id), None)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
            
        # Преобразуем строку с товарами обратно в JSON
        try:
            order['items'] = json.loads(order['items'])
        except:
            order['items'] = []
            
        return jsonify({'status': 'success', 'order': order})
    except Exception as e:
        logging.error(f"Error in get_order: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
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
