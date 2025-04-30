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

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        auth_data = request.json
        print("Получены данные:", auth_data)  # Логируем входящие данные
        
        # Простейшая проверка данных
        if not auth_data or 'id' not in auth_data:
            return jsonify({"status": "error", "message": "Invalid data"}), 400
            
        # Сохраняем данные (упрощённо)
        with open('users.json', 'a') as f:
            f.write(json.dumps(auth_data) + '\n')
            
        return jsonify({
            "status": "success",
            "user": {
                "id": auth_data['id'],
                "name": auth_data.get('first_name', 'User')
            }
        })
    except Exception as e:
        print("Ошибка:", str(e))  # Логируем ошибки
        return jsonify({"status": "error", "message": str(e)}), 500
    @app.before_request
def log_request():
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
