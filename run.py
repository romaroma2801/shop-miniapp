from app import app
from bot import main as start_bot
import threading

if __name__ == "__main__":
    # Запускаем Flask-приложение в отдельном потоке
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.start()

    # Запускаем Telegram-бота в основном потоке
    start_bot()
