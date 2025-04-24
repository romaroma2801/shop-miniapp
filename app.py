from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, origins=[os.getenv("TELEGRAM_WEB_APP_URL")])

SHOP_API_KEY = os.getenv("SHOP_API_KEY", "WWH15wOAGd0PwdBxGLc5nr2X0YGg0ALqXzbRUmpUoyqcpyXNs1RcyL1Hh1XUAKgbd4vmSKfSIrhA4lF4bdCais1F6WziIbcFBjmpzbCYst0Pz11Dyg0wvUrABdKPRlWz4Bd5ZNQD7wd8tNcJALBWQKmCi1kLcUtITtJaJLvAK2zb6bAs4bcxs6cWckd7LQdidT52hLU0xhZm3HXoSa3IrILHba0rSTwnqyCTe7DaPVlbssCUiSmUnJhHbtEMYySG")
@app.route('/api/stores/<city_id>', methods=['GET'])
def get_stores(city_id):
    response = requests.get(
        f'https://api.shop.com/cities/{city_id}/stores',
        headers={'Authorization': f'Bearer {SHOP_API_KEY}'}
    )
    return jsonify(response.json())
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
# Пример эндпоинта для получения областей
@app.route('/api/regions', methods=['GET'])
def get_regions():
    response = requests.get(
        'https://api.shop.com/regions',
        headers={'Authorization': f'Bearer {SHOP_API_KEY}'}
    )
    return jsonify(response.json())

# Пример эндпоинта для получения городов по области
@app.route('/api/cities/<region_id>', methods=['GET'])
def get_cities(region_id):
    response = requests.get(
        f'https://api.shop.com/regions/{region_id}/cities',
        headers={'Authorization': f'Bearer {SHOP_API_KEY}'}
    )
    return jsonify(response.json())

# Главная страница (рендерит фронтенд)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
