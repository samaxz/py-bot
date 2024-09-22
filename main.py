import sqlalchemy
import telebot
from sqlalchemy import MetaData, Table, Column, Integer, String, select

from constants import postg_name, postg_pass, bot_token

DB_URL = f'postgresql://{postg_name}:{postg_pass}@localhost:5432/net_lab_checker'
engine = sqlalchemy.create_engine(DB_URL, echo=True)
meta = MetaData()

phones = Table('phones', meta, Column('id', Integer, primary_key=True), Column('phone', String), )
emails = Table('emails', meta, Column('id', Integer, primary_key=True), Column('email', String), )

bot = telebot.TeleBot(f'{bot_token}')

new_message = ''


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id,
                     "Этот бот используется для проверок телефона и email. Напиши /check_phone или /check_email чтобы начать")


@bot.message_handler(commands=['enter_phone'])
def on_enter_phone(message):
    # bot.send_message(message.from_user.id, "Введи номер телефона")
    # if not message.text.strip():
    #     bot.send_message(message.from_user.id, "Поле не может быть пустым")
    # else:
    #     bot.register_next_step_handler(message, on_check_phone)
    selected_phone = phones.select().where(phones.c.phone == message.text)
    # selected_phone = phones.select().where(phones.c.phone == new_message)
    connection = engine.connect()
    result = connection.execute(selected_phone)

    if result.first() is not None:
        print('phone has been found')
        bot.send_message(message.from_user.id, 'Данный номер присутствует в БД 😀')
    else:
        print('phone is absent')
        bot.send_message(message.from_user.id, 'Данный номер отсутствует в БД ☹️')


@bot.message_handler(commands=['check_phone'])
def on_check_phone(message):
    bot.send_message(message.from_user.id, "Введи номер телефона")
    bot.register_next_step_handler(message, on_enter_phone)
    # if not message.text.strip():
    # 	bot.send_message(message.from_user.id,
    # 					 "Поле не может быть пустым")
    #  message.text.strip():
    # global new_message
    # new_message = message.text
    # selected_phone = phones.select().where(phones.c.phone == message.text)
    # # selected_phone = phones.select().where(phones.c.phone == new_message)
    # connection = engine.connect()
    # result = connection.execute(selected_phone)
    #
    # if result.first() is not None:
    #     print('phone has been found')
    #     bot.send_message(message.from_user.id, 'Данный номер присутствует в БД')
    # else:
    #     print('phone is absent')
    #     bot.send_message(message.from_user.id, 'Данный номер отсутствует в БД')


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	bot.send_message(message.from_user.id, 'Данная команда недоступна. Используй /check_phone или /check_email')
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if (message.text != '/check_phone') or (message.text != '/check_email'):
        bot.send_message(message.from_user.id, "Данная команда недоступна. Используй /check_phone или /check_email")
    elif message.text == '/check_phone':
        # bot.send_message(message.from_user.id, "Введи номер телефона")
        # new_message = message.text
        bot.register_next_step_handler(message, on_enter_phone)


# elif message.text == '/check_email':
# bot.register_next_step_handler(message, on_email_check)
# elif not message.text.strip():
# 	bot.send_message(message.from_user.id, "Поле не может быть пустым")
# elif message.text is '/check_phone':
# selected_phone = phones.select().where(phones.c.phone == message.text)
# connection = engine.connect()
# result = connection.execute(selected_phone)
#
# if result.first() is not None:
# 	print('nayden')
# 	bot.reply_to(message, 'Данный номер присутствует в БД')
# else:
# 	print('absent')
# 	bot.reply_to(message, 'Данный номер отсутствует в БД')

# elif message.text == "/check_phone":
# 	bot.send_message(message.from_user.id, "Напиши номер телефона, который хочешь проверить")
# else:
# 	bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

# bot.send_message(message.from_user.id, 'Данная команда недоступна. Используй /check_phone или /check_email')


bot.infinity_polling()
