import telebot
import os
from flask import Flask, request
import sqlite3  # Для базы данных подписок

# Инициализация бота с токеном из переменной окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен!")
bot = telebot.TeleBot(8267466919:AAFAZ2vCmLwrkFulBPgRauRq3dkpB0FchGM)

# Инициализация Flask
app = Flask(__name__)

# Подключение к базе данных
def init_db():
    conn = sqlite3.connect('subscriptions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                    user_id INTEGER PRIMARY KEY,
                    end_date TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# Функции для работы с базой
def add_subscription(user_id, days):
    import datetime
    conn = sqlite3.connect('subscriptions.db')
    c = conn.cursor()
    c.execute("SELECT end_date FROM subscriptions WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result:
        end_date = datetime.datetime.fromisoformat(result[0])
    else:
        end_date = datetime.datetime.now()
    end_date += datetime.timedelta(days=days)
    c.execute("INSERT OR REPLACE INTO subscriptions (user_id, end_date) VALUES (?, ?)", (user_id, end_date.isoformat()))
    conn.commit()
    conn.close()

def check_subscription(user_id):
    import datetime
    conn = sqlite3.connect('subscriptions.db')
    c = conn.cursor()
    c.execute("SELECT end_date FROM subscriptions WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        end_date = datetime.datetime.fromisoformat(result[0])
        return end_date > datetime.datetime.now()
    return False

# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот фитнес-клуба СПЛИТ. Выберите опцию:\n/subscribe - Купить абонемент\n/status - Проверить подписку")

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("1 месяц - 5000 руб", callback_data="sub_1"))
    markup.add(telebot.types.InlineKeyboardButton("3 месяца - 12000 руб", callback_data="sub_3"))
    markup.add(telebot.types.InlineKeyboardButton("6 месяцев - 20000 руб", callback_data="sub_6"))
    bot.send_message(message.chat.id, "Выберите абонемент:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sub_"))
def callback_subscribe(call):
    days = int(call.data.split("_")[1]) * 30  # Пример: 1 месяц = 30 дней
    price = {"1": 5000, "3": 12000, "6": 20000}[call.data.split("_")[1]]
    # Здесь интегрируйте Яндекс.Деньги (используйте их API для оплаты)
    # Для теста просто добавим подписку после "оплаты"
    add_subscription(call.from_user.id, days)
    bot.send_message(call.message.chat.id, f"Подписка на {days} дней активирована! (Тестовая оплата)")

@bot.message_handler(commands=['status'])
def status(message):
    if check_subscription(message.from_user.id):
        bot.reply_to(message, "Ваша подписка активна.")
    else:
        bot.reply_to(message, "Подписка истекла или не активна.")

# Эндпоинт для пинга (чтобы бот не засыпал)
@app.route('/')
def ping():
    return 'Bot is alive!'

# Эндпоинт для вебхуков Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Bad request', 400

if __name__ == '__main__':
    # Установка вебхука (один раз при запуске)
    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_URL', 'your-bot-name.onrender.com')}/webhook"
    bot.remove_webhook()  # Удаляем старый, если есть
    bot.set_webhook(url=WEBHOOK_URL)
    
    # Запуск Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

