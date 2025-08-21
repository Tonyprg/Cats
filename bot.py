import telebot
import requests
from telebot import types


token = None
host  = None
port  = None

with open('settings.txt') as file:
    settings = eval(file.read())
    token    = settings['token']
    host     = settings['host']
    port     = settings['port']

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['join'])
def join(message):
    try:
        response = requests.get(
            f'http://{host}:{port}/join/{message.from_user.username}')
    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, 'Сервер не запущен')
        return None

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    left   = types.KeyboardButton('left')
    right  = types.KeyboardButton('right')
    up     = types.KeyboardButton('up')
    down   = types.KeyboardButton('down')
    markup.row(up)
    markup.row(left, right)
    markup.row(down)
    bot.send_message(message.chat.id, response.text)
    bot.send_message(message.chat.id,
                     'Куда двигать котенка?',
                     reply_markup=markup)


@bot.message_handler(commands=['coins'])
def coins(message):
    try:
        response = requests.get(
            f'http://{host}:{port}/get_coins/{message.from_user.username}')

        if not response.ok:
            bot.send_message(message.chat.id, 'Сначала создайте котенка.')
            return None

    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, 'Сервер не запущен')
        return None

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    left   = types.KeyboardButton('left')
    right  = types.KeyboardButton('right')
    up     = types.KeyboardButton('up')
    down   = types.KeyboardButton('down')
    markup.row(up)
    markup.row(left, right)
    markup.row(down)
    bot.send_message(message.chat.id, response.text, reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message):

    if message.text not in ['left', 'right', 'up', 'down']:
        bot.send_message(message.chat.id, 'Не удалось распознать сообщение.')
        return None

    name = message.from_user.username
    direction = message.text

    try:
        response = requests.get(
            f'http://{host}:{port}/move/{name}/{direction}')

        if not response.ok:
            bot.send_message(message.chat.id, 'Сначала создайте котенка.')
            return None

        bot.send_message(message.chat.id, {
            'left':  'Котенок идет влево',
            'right': 'Котенок идет вправо',
            'up':    'Котенок идет вверх',
            'down':  'Котенок идет вниз',
        }[direction])

    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, 'Сервер не запущен')
        return None


bot.infinity_polling()
