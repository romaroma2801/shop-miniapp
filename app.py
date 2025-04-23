from flask import Flask, jsonify, request
import requests
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

app = Flask(__name__)

# Токены
TELEGRAM_TOKEN = 'ТВОЙ_ТЕЛЕГРАМ_ТОКЕН'
SHOP_API_KEY = 'ТВОЙ_API_КЛЮЧ_МАГАЗИНА'

# Создание бота
bot = Bot(token=TELEGRAM_TOKEN)

@app.route('/')
def home():
    return "Hello, welcome to the shop mini app!"

@app.route('/start', methods=['POST'])
def start():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, bot)
    dispatcher = Updater(token=TELEGRAM_TOKEN, use_context=True).dispatcher
    dispatcher.process_update(update)
    return "OK"

def get_shop_info():
    # Здесь можно использовать API магазина для получения информации
    response = requests.get('https://api.shop.com/addresses', headers={'Authorization': f'Bearer {SHOP_API_KEY}'})
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

