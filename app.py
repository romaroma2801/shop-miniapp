import os
import json
import logging
import requests as req_lib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# --- Google Sheets Auth ---
def get_gsheets_creds():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = {
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
    }
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

def get_users_sheet():
    client = gspread.authorize(get_gsheets_creds())
    return client.open("USERS").sheet1

def get_orders_sheet():
    client = gspread.authorize(get_gsheets_creds())
    return client.open("ORDERS").sheet1

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

# --- API Routes ---
@app.route('/api/get-user')
def get_user():
    username = request.args.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'No username provided'}), 400
    try:
        sheet = get_users_sheet()
        records = sheet.get_all_records()
        user = next((u for u in records if u.get('Username', '').lower() == username.lower()), None)
        
        if user:
            return jsonify({'status': 'success', 'user': user, 'exists': True})
        else:
            return jsonify({'status': 'success', 'user': {'Username': username, 'Name': '', 'Phone': ''}, 'exists': False})
    except Exception as e:
        logging.error(f"Error in get_user: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.json
        if not data.get('username'):
            return jsonify({'status': 'error', 'message': 'Username is required'}), 400
            
        sheet = get_users_sheet()
        records = sheet.get_all_records()
        user_index = next((i for i, u in enumerate(records) if u.get('Username', '').lower() == data['username'].lower()), None)
        
        if user_index is not None:
            row = user_index + 2
            if data.get('name'): sheet.update_cell(row, 2, data['name'])
            if data.get('phone'): sheet.update_cell(row, 3, data['phone'])
            message = "User updated"
        else:
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

@app.route('/api/catalog')
def get_catalog():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = req_lib.get('https://nekuri.by/parser/output/catalog.json', headers=headers)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            data = {str(item['id']): item for item in data if isinstance(item, dict) and 'id' in item}
        return jsonify(data)
    except Exception as e:
        logging.error(f"Ошибка при загрузке каталога: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/promotions')
def get_promotions():
    try:
        response = req_lib.get('https://nekuri.by/api/news-feed.json')
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        if not data.get('username'):
            return jsonify({'status': 'error', 'message': 'Username is required'}), 400
            
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        
        last_order_id = records[-1].get('order_id', 0) if records else 0
        if not isinstance(last_order_id, int):
            last_order_id = len(records)
        order_id = int(last_order_id) + 1
        
        order_date = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        items_str = json.dumps(data['items'], ensure_ascii=False)
        
        sheet.append_row([
            order_id, data['username'], order_date, items_str,
            data.get('total', 0), data.get('discount', 0), data.get('delivery', 0), data.get('final_total', 0),
            'в обработке', data.get('customer_name', ''), data.get('city', ''), 
            data.get('postcode', ''), data.get('address', ''), data.get('phone', '')
        ])
        
        send_order_notification(order_id, data)
        return jsonify({"status": "success", "order_id": order_id})
    except Exception as e:
        logging.error(f"Error in create_order: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-orders')
def get_orders():
    username = request.args.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'No username provided'}), 400
    try:
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        user_orders = [order for order in records if order.get('username', '').lower() == username.lower()]
        user_orders.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        return jsonify(user_orders)
    except Exception as e:
        logging.error(f"Error in get_orders: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-order/<int:order_id>')
def get_order(order_id):
    try:
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        order = next((o for o in records if o.get('order_id') == order_id), None)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        try:
            order['items'] = json.loads(order['items'])
        except:
            order['items'] = []
        return jsonify({'status': 'success', 'order': order})
    except Exception as e:
        logging.error(f"Error in get_order: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def send_order_notification(order_id, order_data):
    try:
        message = f"🛒 <b>Новый заказ №{order_id}</b>\n"
        message += f"📅 Дата: {(datetime.utcnow() + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M:%S')}\n"
        message += f"👤 Пользователь: @{order_data['username']}\n\n🛍️ <b>Товары:</b>\n"
        for item in order_data['items']:
            message += f"- {item['title']} ({item.get('option', 'Без варианта')}) × {item['quantity']} = {item['price'] * item['quantity']:.2f} BYN\n"
        message += f"\n💰 <b>Итого:</b> {order_data['final_total']:.2f} BYN\n"
        message += f"👤 Клиент: {order_data.get('customer_name', '-')}\n📱 Телефон: {order_data.get('phone', '-')}\n"
        message += f"🏠 Адрес: {order_data.get('city', '')} {order_data.get('address', '')}"
        
        TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') 
        CHAT_ID = '568416622' 
        
        req_lib.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={
            'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'
        })
    except Exception as e:
        logging.error(f"Error sending Telegram notification: {str(e)}")

# --- Telegram Bot via Webhook (БЕЗ python-telegram-bot) ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        update = request.get_json(force=True)
        
        # Проверяем, что это команда /start
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text == '/start':
                web_app_url = os.getenv('RENDER_EXTERNAL_URL', 'https://shop-miniapp.onrender.com')
                
                # Отправляем сообщение с кнопкой Web App
                req_lib.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={
                    'chat_id': chat_id,
                    'text': 'Добро пожаловать в <b>NEKURI</b>! 👋\nНажмите кнопку ниже, чтобы открыть мини-приложение.',
                    'parse_mode': 'HTML',
                    'reply_markup': {
                        'inline_keyboard': [[
                            {
                                'text': '🛒 Открыть магазин',
                                'web_app': {'url': web_app_url}
                            }
                        ]]
                    }
                })
            
            # Обработка текста (поиск города)
            elif text and not text.startswith('/'):
                city = text.strip()
                found = False
                for region, cities in STORE_DATA.items():
                    if city in cities:
                        stores = cities[city]
                        buttons = [[{'text': store["address"], 'url': store.get("map_link", "#")}]]
                        req_lib.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={
                            'chat_id': chat_id,
                            'text': f'Магазины в городе {city}:',
                            'reply_markup': {'inline_keyboard': buttons}
                        })
                        found = True
                        break
                
                if not found:
                    req_lib.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={
                        'chat_id': chat_id,
                        'text': 'Город не найден. Попробуйте снова или откройте Mini App.'
                    })
        
        return 'ok', 200
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        return 'error', 500

# --- Health Check ---
@app.route('/health')
def health():
    return 'OK', 200

# --- Set Webhook on Startup ---
def set_webhook():
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url and BOT_TOKEN:
        try:
            # Удаляем старый webhook
            req_lib.post(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook')
            
            # Устанавливаем новый
            response = req_lib.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook', json={
                'url': f"{webhook_url}/webhook",
                'allowed_updates': ['message', 'callback_query']
            })
            logging.info(f"✅ Webhook set: {response.json()}")
        except Exception as e:
            logging.error(f"❌ Error setting webhook: {str(e)}")

# Вызываем при импорте модуля
set_webhook()

# --- Launch Flask App ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=PORT)
