import os
import subprocess
import sys
from multiprocessing import Process

def run_bot():
    subprocess.run([sys.executable, "bot.py"])

def run_flask():
    subprocess.run([sys.executable, "app.py"])

if __name__ == '__main__':
    bot_process = Process(target=run_bot)
    flask_process = Process(target=run_flask)
    
    bot_process.start()
    flask_process.start()
    
    bot_process.join()
    flask_process.join()
