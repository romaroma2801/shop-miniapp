from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import requests
import json

app = Flask(__name__)
CORS(app, origins=[os.getenv("TELEGRAM_WEB_APP_URL")])

with open('store_full.json', 'r', encoding='utf-8') as file:
    STORE_DATA = json.load(file)
    
SHOP_API_KEY = os.getenv("SHOP_API_KEY", "WWH15wOAGd0PwdBxGLc5nr2X0YGg0ALqXzbRUmpUoyqcpyXNs1RcyL1Hh1XUAKgbd4vmSKfSIrhA4lF4bdCais1F6WziIbcFBjmpzbCYst0Pz11Dyg0wvUrABdKPRlWz4Bd5ZNQD7wd8tNcJALBWQKmCi1kLcUtITtJaJLvAK2zb6bAs4bcxs6cWckd7LQdidT52hLU0xhZm3HXoSa3IrILHba0rSTwnqyCTe7DaPVlbssCUiSmUnJhHbtEMYySG")
# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница выбора областей
@app.route('/regions')
def regions():
    regions = list(STORE_DATA.keys())
    return render_template('regions.html', regions=regions)

# Страница выбора городов
@app.route('/cities/<region>')
def cities(region):
    cities = list(STORE_DATA.get(region, {}).keys())
    return render_template('cities.html', region=region, cities=cities)

# Страница выбора магазинов
@app.route('/stores/<region>/<city>')
def stores(region, city):
    stores = STORE_DATA.get(region, {}).get(city, [])
    return render_template('stores.html', region=region, city=city, stores=stores)

# Страница с деталями магазина
@app.route('/store/<region>/<city>/<store_name>')
def store_details(region, city, store_name):
    stores = STORE_DATA.get(region, {}).get(city, [])
    store = next((s for s in stores if s['name'] == store_name), None)
    if store:
        return render_template('store_details.html', store=store)
    return "Магазин не найден", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
