import os
import subprocess
import sys
from multiprocessing import Process
import time
import psutil

def kill_previous_processes():
    """Убивает предыдущие процессы бота"""
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if ('python' in proc.info['name'].lower() or 
                'python' in (proc.info['cmdline'] or [])):
                if 'bot.py' in (proc.info['cmdline'] or []) and proc.info['pid'] != current_pid:
                    proc.kill()
                    print(f"Killed previous bot process: {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def run_bot():
    time.sleep(5)
    subprocess.Popen(["python", "bot.py"])

def run_flask():
    subprocess.run([sys.executable, "app.py"])

if __name__ == '__main__':
    kill_previous_processes()
    
    bot_process = Process(target=run_bot)
    flask_process = Process(target=run_flask)
    
    bot_process.start()
    time.sleep(5)  # Даем боту время на инициализацию
    flask_process.start()
    
    try:
        bot_process.join()
        flask_process.join()
    except KeyboardInterrupt:
        bot_process.terminate()
        flask_process.terminate()
