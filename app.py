from flask import Flask, jsonify, render_template, send_from_directory
import os
import json

app = Flask(__name__)

# Загрузка данных о магазинах из файла store_full.json
with open('store_full.json', 'r', encoding='utf-8') as file:
    STORE_DATA = json.load(file)

# Эндпоинт для получения списка областей
@app.route('/api/regions', methods=['GET'])
def get_regions():
    regions = list(STORE_DATA.keys())
    return jsonify(regions)

# Эндпоинт для получения списка городов по выбранной области
@app.route('/api/cities/<region>', methods=['GET'])
def get_cities(region):
    cities = list(STORE_DATA.get(region, {}).keys())
    return jsonify(cities)

# Эндпоинт для получения списка магазинов по выбранному региону и городу
@app.route('/api/stores/<region>/<city>', methods=['GET'])
def get_stores(region, city):
    stores = STORE_DATA.get(region, {}).get(city, [])
    return jsonify(stores)

# Служебный эндпоинт для обслуживания статических файлов (иконки, CSS, JS)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Главная страница (рендерит фронтенд)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
