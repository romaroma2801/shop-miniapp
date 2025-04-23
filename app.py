from flask import Flask, jsonify, request
import requests
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

app = Flask(__name__)

# Токены
TELEGRAM_TOKEN = 7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns
SHOP_API_KEY = WWH15wOAGd0PwdBxGLc5nr2X0YGg0ALqXzbRUmpUoyqcpyXNs1RcyL1Hh1XUAKgbd4vmSKfSIrhA4lF4bdCais1F6WziIbcFBjmpzbCYst0Pz11Dyg0wvUrABdKPRlWz4Bd5ZNQD7wd8tNcJALBWQKmCi1kLcUtITtJaJLvAK2zb6bAs4bcxs6cWckd7LQdidT52hLU0xhZm3HXoSa3IrILHba0rSTwnqyCTe7DaPVlbssCUiSmUnJhHbtEMYySG

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

