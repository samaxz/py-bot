import sqlalchemy
import telebot
from sqlalchemy import MetaData, Table, Column, Integer, String, select

from constants import postg_name, postg_pass, bot_token

DB_URL = f'postgresql://{postg_name}:{postg_pass}@localhost:5432/net_lab_checker'
engine = sqlalchemy.create_engine(DB_URL, echo=True)
meta = MetaData()

phones = Table('phones', meta, Column('id', Integer, primary_key=True), Column('phone', String), )
emails = Table('emails', meta, Column('id', Integer, primary_key=True), Column('email', String), )

connection = engine.connect()

bot = telebot.TeleBot(f'{bot_token}')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id,
                     "Этот бот используется для проверок телефона и email. Напиши /check_phone или /check_email чтобы начать")


@bot.message_handler(commands=['check_phone'])
def on_check_phone(message):
    bot.send_message(message.from_user.id, "Введи номер телефона")
    bot.register_next_step_handler(message, on_enter_phone)


@bot.message_handler(commands=['enter_phone'])
def on_enter_phone(message):
    selected_phone = phones.select().where(phones.c.phone == message.text.strip())
    result = connection.execute(selected_phone)

    if result.first() is not None:
        print('phone has been found')
        bot.send_message(message.from_user.id, 'Данный номер присутствует в БД 😀')
    else:
        print('phone is absent')
        bot.send_message(message.from_user.id, 'Данный номер отсутствует в БД ☹️')


@bot.message_handler(commands=['check_email'])
def on_check_phone(message):
    bot.send_message(message.from_user.id, "Введи email")
    bot.register_next_step_handler(message, on_enter_email)


@bot.message_handler(commands=['enter_email'])
def on_enter_email(message):
    selected_email = emails.select().where(emails.c.email == message.text.strip())
    result = connection.execute(selected_email)

    if result.first() is not None:
        print('email has been found')
        bot.send_message(message.from_user.id, 'Данный email присутствует в БД 😀')
    else:
        print('email is absent')
        bot.send_message(message.from_user.id, 'Данный email отсутствует в БД ☹️')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if (message.text != '/check_phone') or (message.text != '/check_email'):
        bot.send_message(message.from_user.id, "Данная команда недоступна. Используй /check_phone или /check_email")


bot.infinity_polling()
