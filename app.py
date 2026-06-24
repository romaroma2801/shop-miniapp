import os
import json
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Flask App ---
app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        "private_key": os.getenv("GSHEETS_PRIVATE_KEY", "").replace('\\n', '\n'),
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

# --- Главная страница ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API: Каталог ---
@app.route('/api/catalog')
def get_catalog():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://nekuri.by/parser/output/catalog.json', headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            data = {str(item['id']): item for item in data if isinstance(item, dict) and 'id' in item}
        return jsonify(data)
    except Exception as e:
        logging.error(f"Ошибка каталога: {e}")
        return jsonify({"error": str(e)}), 500

# --- API: Пользователь ---
@app.route('/api/get-user')
def get_user():
    username = request.args.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'No username'}), 400
    try:
        sheet = get_users_sheet()
        records = sheet.get_all_records()
        user = next((u for u in records if u.get('Username', '').lower() == username.lower()), None)
        
        if user:
            return jsonify({'status': 'success', 'user': user, 'exists': True})
        else:
            return jsonify({'status': 'success', 'user': {'Username': username, 'Name': '', 'Phone': ''}, 'exists': False})
    except Exception as e:
        logging.error(f"Error get_user: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.json
        if not data.get('username'):
            return jsonify({'status': 'error', 'message': 'Username required'}), 400
            
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
        logging.error(f"Error save_user: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- API: Заказы ---
@app.route('/api/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        if not data.get('username'):
            return jsonify({'status': 'error', 'message': 'Username required'}), 400
            
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        
        last_order_id = records[-1].get('order_id', 0) if records else 0
        if not isinstance(last_order_id, int):
            try:
                last_order_id = int(last_order_id)
            except:
                last_order_id = len(records)
        order_id = int(last_order_id) + 1
        
        order_date = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        items_str = json.dumps(data['items'], ensure_ascii=False)
        
        sheet.append_row([
            order_id, 
            data['username'], 
            order_date, 
            items_str,
            data.get('total', 0), 
            data.get('discount', 0), 
            data.get('delivery', 0), 
            data.get('final_total', 0),
            'в обработке', 
            data.get('customer_name', ''), 
            data.get('city', ''), 
            data.get('postcode', ''), 
            data.get('address', ''), 
            data.get('phone', '')
        ])
        
        send_admin_notification(order_id, data)
        send_user_notification(data['username'], order_id, data)
        
        return jsonify({"status": "success", "order_id": order_id})
    except Exception as e:
        logging.error(f"Error create_order: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-orders')
def get_orders():
    username = request.args.get('username')
    if not username:
        return jsonify({'status': 'error', 'message': 'No username'}), 400
    try:
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        user_orders = [o for o in records if o.get('username', '').lower() == username.lower()]
        user_orders.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        return jsonify(user_orders)
    except Exception as e:
        logging.error(f"Error get_orders: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-order/<int:order_id>')
def get_order(order_id):
    try:
        sheet = get_orders_sheet()
        records = sheet.get_all_records()
        order = next((o for o in records if int(o.get('order_id', 0)) == order_id), None)
        if not order:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        try:
            order['items'] = json.loads(order.get('items', '[]'))
        except:
            order['items'] = []
        return jsonify({'status': 'success', 'order': order})
    except Exception as e:
        logging.error(f"Error get_order: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Уведомления ---
def send_admin_notification(order_id, data):
    try:
        msg = f"🛒 <b>Новый заказ №{order_id}</b>\n\n"
        msg += f"👤 @{data['username']}\n\n"
        msg += "🛍️ <b>Товары:</b>\n"
        for item in data['items']:
            msg += f"• {item['title']} × {item['quantity']} = {float(item['price']) * int(item['quantity']):.2f} BYN\n"
        msg += f"\n💰 Итого: {float(data['final_total']):.2f} BYN\n"
        msg += f"👤 {data.get('customer_name', '-')}\n"
        msg += f"📱 {data.get('phone', '-')}\n"
        msg += f"🏠 {data.get('city', '')} {data.get('address', '')}"
        
        requests.post(f'https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}/sendMessage', json={
            'chat_id': '568416622', 'text': msg, 'parse_mode': 'HTML'
        })
    except Exception as e:
        logging.error(f"Admin notification error: {e}")

def send_user_notification(username, order_id, data):
    try:
        msg = f"✅ <b>Заказ №{order_id} принят!</b>\n\n"
        msg += "🛍️ Товары:\n"
        for item in data['items']:
            msg += f"• {item['title']} × {item['quantity']}\n"
        msg += f"\n💰 Итого: {float(data['final_total']):.2f} BYN\n"
        msg += "📦 Статус: В обработке"
        
        requests.post(f'https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}/sendMessage', json={
            'chat_id': f'@{username}', 'text': msg, 'parse_mode': 'HTML'
        })
    except Exception as e:
        logging.error(f"User notification error: {e}")

# --- Telegram Bot ---
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        update = request.get_json(force=True)
        
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text == '/start':
                web_app_url = os.getenv('WEB_APP_URL', 'https://shop-miniapp.onrender.com')
                
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={
                    'chat_id': chat_id,
                    'text': '👋 Добро пожаловать в <b>NEKURI</b>!\n\nНажми кнопку ниже, чтобы открыть магазин.',
                    'parse_mode': 'HTML',
                    'reply_markup': {
                        'inline_keyboard': [[{
                            'text': '🛒 Открыть магазин',
                            'web_app': {'url': web_app_url}
                        }]]
                    }
                })
        
        return 'ok', 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return 'error', 500

@app.route('/health')
def health():
    return 'OK', 200

# --- Установка webhook при старте ---
def set_webhook():
    webhook_url = os.getenv('WEBHOOK_URL', 'https://shop-miniapp.onrender.com/webhook')
    if webhook_url and BOT_TOKEN:
        try:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook')
            r = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook', json={
                'url': webhook_url,
                'allowed_updates': ['message']
            })
            logging.info(f"✅ Webhook установлен: {r.json()}")
        except Exception as e:
            logging.error(f"❌ Ошибка установки webhook: {e}")

# Вызываем при импорте модуля (для Render)
set_webhook()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
