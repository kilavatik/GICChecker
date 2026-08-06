import telebot
import os
from dotenv import load_dotenv
import time
import threading
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup as bs

load_dotenv()   # загружаем переменные из .env

DATE_FILE = "last_date.txt"

def save_date(date_obj):
    if date_obj is None:
        with open(DATE_FILE, 'w') as f:
            f.write('')
        return
    with open(DATE_FILE, 'w') as f:
        f.write(date_obj.isoformat())

def load_date():
    if not os.path.exists(DATE_FILE):
        return None
    with open(DATE_FILE, 'r') as f:
        date_str = f.read().strip()
    if date_str == '':
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
global act_date
bot = telebot.TeleBot(TOKEN)

def check_condition():
    act_date = load_date()
    if act_date is None:
        act_date = date(2006, 12, 4)

    url = "https://pinsk.gov.by/about/info/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return False

    soup = bs(r.text, "html.parser")
    all_news = soup.find_all('div', class_='news-item')

    for x in all_news:
        try:
            img = x.find('a').find('img')
            if img and img.get('title') == "Вниманию граждан, нуждающихся в улучшении жилищных условий!":
                d = x.find("div", class_="news-item-date").text.strip()
                # Правильный парсинг даты (день, месяц, год)
                day, month, year = map(int, d.split("."))
                new_date = date(year, month, day)
                if act_date < new_date:
                    save_date(new_date)
                    return True
        except Exception as e:
            print(f"Ошибка парсинга элемента: {e}")
            continue
    return False

def send_message_if_condition():
    while True:
        try:
            if check_condition():
                for _ in range(10):
                    str = "АТАС, ПИЗДА, КВ ВЫЛОЖИЛИ "+str(act_date)
                    bot.send_message(CHAT_ID, "АТАС, ПИЗДА, КВ ВЫЛОЖИЛИ")
            else:
                print(f"{datetime.now()}: Условие не выполнено, пропускаем.")
        except Exception as e:
            print(f"Ошибка в цикле: {e}")
        time.sleep(10)  # ждём час

# Запускаем поток для проверки
thread = threading.Thread(target=send_message_if_condition, daemon=True)
thread.start()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен! Будет отправлять сообщения каждый час при условии.")

# Удаляем вебхук (если был) и запускаем polling
bot.remove_webhook()
print("Бот запущен...")

import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_web_server():
    """Запускает минимальный веб-сервер, чтобы Render видел открытый порт."""
    port = int(os.environ.get("PORT", 8080))
    # Важно: слушаем на 0.0.0.0, чтобы принимать запросы извне[reference:4]
    app.run(host='0.0.0.0', port=port, debug=False)

# Запускаем веб-сервер в отдельном потоке, чтобы не блокировать бота
import threading
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# ... ваш код с bot.polling() ...

bot.polling(none_stop=True)
