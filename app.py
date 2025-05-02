from flask import Flask, jsonify, render_template
import os
import json
import logging
import requests

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# Загрузка данных магазинов
try:
    with open('store_full.json', 'r', encoding='utf-8') as file:
        STORE_DATA = json.load(file)
    logging.info("Store data loaded successfully")
except Exception as e:
    logging.error(f"Failed to load store data: {e}")
    STORE_DATA = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/regions', methods=['GET'])
def get_regions():
    try:
        regions = list(STORE_DATA.keys())
        return jsonify(regions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cities/<region>', methods=['GET'])
def get_cities(region):
    try:
        cities = list(STORE_DATA.get(region, {}).keys())
        return jsonify(cities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stores/<region>/<city>', methods=['GET'])
def get_stores(region, city):
    try:
        stores = STORE_DATA.get(region, {}).get(city, [])
        return jsonify(stores)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    try:
        response = requests.get('https://nekuri.by/api/news-feed.php')
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=PORT)
