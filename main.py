import telebot
import os
from dotenv import load_dotenv
import time
import threading
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup as bs

load_dotenv()   # ищет .env в текущей папке

DATE_FILE = "last_date.txt"   # файл, где будет храниться дата
# ======================

def save_date(date_obj):
    """
    Сохраняет объект date (год, месяц, день) в файл.
    Если передан None, файл очищается.
    """
    if date_obj is None:
        with open(DATE_FILE, 'w') as f:
            f.write('')
        return

    # Сохраняем в формате ГГГГ-ММ-ДД (ISO-формат для даты)
    with open(DATE_FILE, 'w') as f:
        f.write(date_obj.isoformat())

def load_date():
    """
    Загружает дату из файла и возвращает объект date.
    Если файла нет или он пуст, возвращает None.
    """
    if not os.path.exists(DATE_FILE):
        return None

    with open(DATE_FILE, 'r') as f:
        date_str = f.read().strip()

    if date_str == '':
        return None

    try:
        # Восстанавливаем дату из ISO-строки (ГГГГ-ММ-ДД)
        return date.fromisoformat(date_str)
    except ValueError:
        return None


TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")   # можно узнать через /start

bot = telebot.TeleBot(TOKEN)

# Условие, которое проверяется каждый час
def check_condition():
    url= "https://pinsk.gov.by/about/info/news/"
    r = requests.get(url)
    soup = bs(r.text, "html.parser")
    all_news = soup.find_all('div', class_='news-item')
    if load_date() is None:
        act_date = date(2006, 12, 4)#ДОДЕЛАЙ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    else:
        act_date = load_date()
    print(act_date)
    for x in all_news:
        try:
            if x.find('a').find('img').get('title') == "Вниманию граждан, нуждающихся в улучшении жилищных условий!":
                d = x.find("div", class_= "news-item-date").text
                new_date = date(int(d.split(".")[2]), int(d.split(".")[1].replace("0", "")), int(d.split(".")[0].replace("0", "")))
                if act_date < new_date:
                    print("АТАС, ПИЗДА, КВ ВЫЛОЖИЛИ")
                    act_date = new_date
                    save_date(act_date)
                    return True               
        except:
                continue
    return False

def send_message_if_condition():
    while True:
        try:
            if check_condition():
                x = 0
                while x<10:
                    bot.send_message(CHAT_ID, "АТАС, ПИЗДА, КВ ВЫЛОЖИЛИ")
                    x+=1
            else:
                print("Условие не выполнено, пропускаем.")
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(3600)  # ждем час

# Запускаем поток для проверки
thread = threading.Thread(target=send_message_if_condition, daemon=True)
thread.start()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен! Будет отправлять сообщения каждый час при условии.")

# Запуск бота (основной поток)
bot.polling(none_stop=True)


