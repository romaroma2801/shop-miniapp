from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import requests
import json
from flask import request, make_response
import uuid

app = Flask(__name__)
CORS(app, origins=[os.getenv("TELEGRAM_WEB_APP_URL")])

with open('store_full.json', 'r', encoding='utf-8') as file:
    STORE_DATA = json.load(file)
    
SHOP_API_KEY = os.getenv("SHOP_API_KEY", "WWH15wOAGd0PwdBxGLc5nr2X0YGg0ALqXzbRUmpUoyqcpyXNs1RcyL1Hh1XUAKgbd4vmSKfSIrhA4lF4bdCais1F6WziIbcFBjmpzbCYst0Pz11Dyg0wvUrABdKPRlWz4Bd5ZNQD7wd8tNcJALBWQKmCi1kLcUtITtJaJLvAK2zb6bAs4bcxs6cWckd7LQdidT52hLU0xhZm3HXoSa3IrILHba0rSTwnqyCTe7DaPVlbssCUiSmUnJhHbtEMYySG")
# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница выбора областей и городов
@app.route('/regions')
def regions():
    return render_template('regions.html')

# API для получения данных
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
# Добавьте в начало файла
from flask import request, make_response
import uuid

# Добавьте после существующих роутов
@app.route('/api/auth/telegram', methods=['POST'])
def handle_telegram_auth():
    try:
        auth_data = request.json
        required_fields = ['id', 'first_name', 'auth_date', 'hash']
        
        if not all(field in auth_data for field in required_fields):
            return jsonify({"error": "Invalid data"}), 400
        
        # Здесь должна быть проверка хэша (пропущено для упрощения)
        # Реальная реализация: https://core.telegram.org/widgets/login#checking-authorization
        
        # Сохраняем пользователя
        user_data = {
            "user_id": auth_data['id'],
            "username": auth_data.get('username'),
            "first_name": auth_data.get('first_name'),
            "last_name": auth_data.get('last_name'),
            "auth_date": auth_data['auth_date'],
            "session_id": str(uuid.uuid4())
        }
        
        # Сохраняем в файл (в реальном проекте - база данных)
        try:
            with open('users.json', 'r+') as f:
                users = json.load(f)
                users.append(user_data)
                f.seek(0)
                json.dump(users, f, indent=2)
        except FileNotFoundError:
            with open('users.json', 'w') as f:
                json.dump([user_data], f, indent=2)
        
        return jsonify({"status": "success", "session_id": user_data['session_id']})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
