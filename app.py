from flask import Flask, jsonify, render_template, request, make_response
from flask_cors import CORS
import os
import requests
import json
import uuid
app = Flask(__name__)
CORS(app, origins=[os.getenv("TELEGRAM_WEB_APP_URL")])

# Инициализация users.json
USER_DATA_PATH = os.path.join(os.getcwd(), 'users.json')
if not os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, 'w') as f:
        json.dump([], f)  # Создаем файл с пустым массивом
CORS(app, origins=[os.getenv("TELEGRAM_WEB_APP_URL")])

with open('store_full.json', 'r', encoding='utf-8') as file:
    STORE_DATA = json.load(file)
    
SHOP_API_KEY = os.getenv("SHOP_API_KEY", "WWH15wOAGd0PwdBxGLc5nr2X0YGg0ALqXzbRUmpUoyqcpyXNs1RcyL1Hh1XUAKgbd4vmSKfSIrhA4lF4bdCais1F6WziIbcFBjmpzbCYst0Pz11Dyg0wvUrABdKPRlWz4Bd5ZNQD7wd8tNcJALBWQKmCi1kLcUtITtJaJLvAK2zb6bAs4bcxs6cWckd7LQdidT52hLU0xhZm3HXoSa3IrILHba0rSTwnqyCTe7DaPVlbssCUiSmUnJhHbtEMYySG")

@app.before_request
def log_request():
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/regions')
def regions():
    return render_template('regions.html')

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
        print("[SERVER] Получен запрос на /api/save-user")
        auth_data = request.json
        print("[SERVER] Данные:", auth_data)
        
        if not auth_data or 'id' not in auth_data:
            return jsonify({"status": "error", "message": "Invalid data"}), 400
        
        # Проверяем, существует ли файл
        if not os.path.exists(USER_DATA_PATH):
            with open(USER_DATA_PATH, 'w') as f:
                json.dump([], f)
        
        # Читаем текущих пользователей
        users = []
        try:
            with open(USER_DATA_PATH, 'r') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = []
        
        # Проверяем, есть ли пользователь уже в базе
        user_exists = any(user.get('id') == auth_data['id'] for user in users)
        
        if not user_exists:
            users.append(auth_data)
            with open(USER_DATA_PATH, 'w') as f:
                json.dump(users, f, indent=2)
            print(f"[SERVER] Пользователь {auth_data['id']} сохранён")
        else:
            print(f"[SERVER] Пользователь {auth_data['id']} уже существует")
        
        return jsonify({
            "status": "success",
            "user": {
                "id": auth_data['id'],
                "first_name": auth_data.get('first_name', ''),
                "last_name": auth_data.get('last_name', ''),
                "username": auth_data.get('username', 'не указан'),
                "phone": auth_data.get('phone', 'не указан')
            }
        })
    
    except Exception as e:
        print("[SERVER ERROR]", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
