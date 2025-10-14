import telebot
from telebot import types
import flask
import os
import logging

# Настройка логирования (выводит информацию в консоль)
logging.basicConfig(level=logging.INFO)

# Переменные из окружения (установите в платформе: TELEGRAM_BOT_TOKEN и WEBHOOK_URL)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

bot = telebot.TeleBot(BOT_TOKEN)
app = flask.Flask(__name__)

# Устанавливаем webhook при запуске (только если URL задан)
if WEBHOOK_URL:
    bot.set_webhook(url=WEBHOOK_URL)

# Эндпоинт для обработки обновлений от Telegram (POST запросы)
@app.route('/', methods=['POST'])
def webhook():
    update = flask.request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return '', 200

# Эндпоинт для проверки статуса (GET, опционально для браузера)
@app.route('/', methods=['GET'])
def index():
    return 'Бот работает! Webhook: ' + (WEBHOOK_URL or 'не задан')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        choose_button = types.InlineKeyboardButton(text="Выбрать абонемент", callback_data="choose_subscription")  # Здесь "товары" – это абонементы
        keyboard.add(choose_button)
        
        bot.send_message(
            message.chat.id,
            "Здравствуй, Дорогой клиент! Хочешь оплатить абонемент в СПЛИТ?",  # Сообщение про абонементы
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка в start_message: {e}")

# Обработчик callback-данных (включая нажатия на inline-кнопки)
@bot.callback_query_handler(func=lambda call: call.data == "choose_subscription")
def callback_choose_subscription(call):
    try:
        show_subscriptions(call.message)  # Вызываем функцию показа абонементов (товаров)
        bot.answer_callback_query(call.id)  # Подтверждаем обработку callback
    except Exception as e:
        logging.error(f"Ошибка в callback_choose_subscription: {e}")

# Функция отображения списка абонементов (здесь "товары" — абонементы)
def show_subscriptions(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        
        # Структура абонементов (ваши ссылки остались без изменений) — это список товаров с URL для покупки
        subscriptions = [
            {"name": "Basic 12 + 60 дней заморозки", "url": "https://pay.ya.ru/t/batX5N"},  # Товар 1
            {"name": "Basic 12", "url": "https://pay.ya.ru/t/HEJkrP"},  # Товар 2
            {"name": "Basic 10", "url": "https://pay.ya.ru/t/cxpkRc"},  # И т.д.
            {"name": "Basic 6", "url": "https://pay.ya.ru/t/rywVP2"},  
            {"name": "Basic 4", "url": "https://pay.ya.ru/t/aFM0Le"},
            {"name": "Basic 3", "url": "https://pay.ya.ru/t/VS40Pc"}, 
            {"name": "Basic 1", "url": "https://pay.ya.ru/t/MjrJ0V"}
        ]  # Здесь товары (абонементы) — список словарей с name и url
        
        for sub in subscriptions:  # Цикл по товарам
            button = types.InlineKeyboardButton(
                text=sub['name'],  # Название товара
                url=sub['url']     # Ссылка на оплату товара
            )
            keyboard.add(button)
        
        bot.send_message(
            message.chat.id,
            "Выберите абонемент:",  # "Выберите товар:"
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Ошибка в show_subscriptions: {e}")

# Запуск сервера (для локального теста в prod — webhook через Flask)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)  # debug=False для продакшена
