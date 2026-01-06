import telebot
from telebot import types
import os
from flask import Flask, request

# Токен: рекомендуется использовать переменную окружения для безопасности
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or '8267466919:AAFAZ2vCmLwrkFulBPgRauRq3dkpB0FchGM'  # Вставьте ваш токен в кавычках# Если не хотите переменную окружения, раскомментируйте ниже (но не для продакшена):
# TOKEN = '8267466919:AAFAZ2vCmLwrkFulBPgRauRq3dkpB0FchGM'

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не задан")

bot = telebot.TeleBot(TOKEN)  # Используем переменную TOKEN (без кавычек внутри)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Здравствуй, дорогой клиент! Хочешь оплатить абонемент в СПЛИТ?")
    show_subscriptions(message)

def show_subscriptions(message):
    keyboard = types.InlineKeyboardMarkup()
    subscriptions = [
        {"name": "Basic 15", "url": "https://pay.ya.ru/t/Zr3OLU"},
        {"name": "Basic 12 + 1 месяц в подарок", "url": "https://pay.ya.ru/t/YLBOjy"},
        {"name": "Basic 9 + 90 дней заморозки", "url": "https://pay.ya.ru/t/8TTUDO"},
        {"name": "Basic 7 + 1 месяц в подарок", "url": "https://pay.ya.ru/t/YoSFhl"},
        {"name": "Basic 6", "url": "https://pay.ya.ru/t/ZjWeqk"},
        {"name": "Basic 3", "url": "https://pay.ya.ru/t/Zzh81U"},
        {"name": "Блок тренировок к Тренеру", "url": "https://pay.ya.ru/t/h0xbkS"},
        {"name": "Блок тренировок СПЛИТ(2 Человека) у Тренера", "url": "https://pay.ya.ru/t/xlkYbD"}
        
    ]
    
    for sub in subscriptions:
        button = types.InlineKeyboardButton(
            text=sub['name'],
            url=sub['url']
        )
        keyboard.add(button)
    
    bot.send_message(
        message.chat.id,
        "Выберите абонемент:",
        reply_markup=keyboard
    )

# Обработка вебхуков
@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegram-bot-split.onrender.com/' + TOKEN)  # Добавлен слэш перед TOKEN
    return 'Webhook set!', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
