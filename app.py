from flask import Flask, jsonify, render_template
import os
import json
import logging
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Загрузите credentials.json в Render (Environment Variables)
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
    return client.open("USERS").sheet1  # Название таблицы

# Пример сохранения данных
@app.route('/api/save-user', methods=['POST'])
def save_user():
    data = request.json
    sheet = get_sheet()
    sheet.append_row([
        data["username"],
        data["name"],
        data["phone"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])
    return jsonify({"status": "success"})
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
