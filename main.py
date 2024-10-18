import platform
import re
import socket
import uuid
from datetime import datetime

import cpuinfo
import psutil
import sqlalchemy
import telebot
from sqlalchemy import MetaData, Table, Column, Integer, String, insert
from sqlalchemy.orm import declarative_base, sessionmaker

from constants import postg_name, postg_pass, bot_token

DB_URL = f'postgresql://{postg_name}:{postg_pass}@localhost:5432/net_lab_checker'
engine = sqlalchemy.create_engine(DB_URL, echo=True)
meta = MetaData()
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

phones = Table('phones', meta, Column('id', Integer, primary_key=True), Column('phone', String), )
emails = Table('emails', meta, Column('id', Integer, primary_key=True), Column('email', String), )

connection = engine.connect()

bot = telebot.TeleBot(f'{bot_token}')

saved_phone = ''


class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id,
                     f"""Этот бот используется для проверок телефона, email, пароля и отображения характеристик девайса. 
Используй {'/check_phone'}, {'/check_email'}, {'/check_password'}, {'/check_specs'} или {'/check_or_add_phone'}, чтобы начать""")


@bot.message_handler(commands=['check_phone'])
def on_check_phone(message):
    bot.send_message(message.from_user.id, "Введи номер телефона")
    bot.register_next_step_handler(message, on_enter_phone)


@bot.message_handler(commands=['enter_phone'])
def on_enter_phone(message):
    match = re.fullmatch(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                         message.text.strip())
    if not match:
        bot.send_message(message.from_user.id, "Введи корректный номер телефона")
        bot.register_next_step_handler(message, on_enter_phone)
        return

    selected_phone = phones.select().where(phones.c.phone == message.text.strip())
    result = connection.execute(selected_phone)

    if result.first() is not None:
        bot.send_message(message.from_user.id, 'Данный номер присутствует в БД 😀')
    else:
        bot.send_message(message.from_user.id, 'Данный номер отсутствует в БД ☹️')


@bot.message_handler(commands=['check_email'])
def on_check_phone(message):
    bot.send_message(message.from_user.id, "Введи email")
    bot.register_next_step_handler(message, on_enter_email)


@bot.message_handler(commands=['enter_email'])
def on_enter_email(message):
    match = re.fullmatch(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                         message.text.strip())
    if not match:
        bot.send_message(message.from_user.id, "Введи корректный email")
        bot.register_next_step_handler(message, on_enter_email)
        return

    selected_email = emails.select().where(emails.c.email == message.text.strip())
    result = connection.execute(selected_email)

    if result.first() is not None:
        bot.send_message(message.from_user.id, 'Данный email присутствует в БД 😀')
    else:
        bot.send_message(message.from_user.id, 'Данный email отсутствует в БД ☹️')


@bot.message_handler(commands=['check_password'])
def on_check_password(message):
    bot.send_message(message.from_user.id, "Введи пароль")
    bot.register_next_step_handler(message, on_enter_password)


@bot.message_handler(commands=['enter_password'])
def on_enter_password(message):
    digits = '1234567890'
    upper_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lower_letters = 'abcdefghijklmnopqrstuvwxyz'
    symbols = '!@#$%^&*()-+'
    acceptable = digits + upper_letters + lower_letters + symbols
    password = message.text.strip()
    passwd = set(password)

    if any(char not in acceptable for char in passwd):
        bot.send_message(message.from_user.id, 'Уупс, был введён запрещённый символ - введи другой пароль')
        bot.register_next_step_handler(message, on_enter_password)
    else:
        recommendations = []
        if len(password) < 8:
            recommendations.append(f'увеличить число символов - {12 - len(password)}')
            bot.send_message(message.from_user.id, 'Слишком короткий пароль, попробуй ввести другой')
            bot.register_next_step_handler(message, on_enter_password)
            return

        for what, errMessage in ((digits, 'цифру'),
                                 (symbols, 'спецсимвол'),
                                 (upper_letters, 'заглавную букву'),
                                 (lower_letters, 'строчную букву')):
            if all(char not in what for char in passwd):
                recommendations.append(f'Добавь 1 {errMessage}')

        if recommendations:
            bot.send_message(message.from_user.id, f"Слабый пароль. Рекомендации:")
            for recommendation in recommendations:
                bot.send_message(message.from_user.id, f"{recommendation}")

        else:
            bot.send_message(message.from_user.id, 'Хороший пароль, nice job 😉')


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


@bot.message_handler(commands=['check_specs'])
def system_information(message):
    # отправляет сообщение
    bot.send_message(message.from_user.id, f"****System Information****")
    # создаёт экземпляр класса
    uname = platform.uname()
    # отправляет сообщения с данными о разных системных характеристиках
    bot.send_message(message.from_user.id, f"System: {uname.system}")
    bot.send_message(message.from_user.id, f"Node Name: {uname.node}")
    bot.send_message(message.from_user.id, f"Release: {uname.release}")
    bot.send_message(message.from_user.id, f"Version: {uname.version}")
    bot.send_message(message.from_user.id, f"Machine: {uname.machine}")
    bot.send_message(message.from_user.id, f"Processor: {uname.processor}")
    bot.send_message(message.from_user.id, f"Processor: {cpuinfo.get_cpu_info()['brand_raw']}")
    bot.send_message(message.from_user.id, f"Ip-Address: {socket.gethostbyname(socket.gethostname())}")
    bot.send_message(message.from_user.id, f"Mac-Address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}")

    # Boot Time - время включения
    bot.send_message(message.from_user.id, '***Boot time***')
    # дата и время включения
    boot_time_timestamp = psutil.boot_time()
    # преобразование строки к объекту date time
    bt = datetime.fromtimestamp(boot_time_timestamp)
    bot.send_message(message.from_user.id,
                     f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # print CPU information
    bot.send_message(message.from_user.id, "CPU Info")
    # number of cores
    bot.send_message(message.from_user.id, f"Physical cores: {psutil.cpu_count(logical=False)}")
    bot.send_message(message.from_user.id, f"Total cores: {psutil.cpu_count(logical=True)}")
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    bot.send_message(message.from_user.id, f"Max Frequency: {cpufreq.max:.2f}Mhz")
    bot.send_message(message.from_user.id, f"Min Frequency: {cpufreq.min:.2f}Mhz")
    bot.send_message(message.from_user.id, f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    bot.send_message(message.from_user.id, "CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        bot.send_message(message.from_user.id, f"Core {i}: {percentage}%")
    bot.send_message(message.from_user.id, f"Total CPU Usage: {psutil.cpu_percent()}%")

    # Memory Information
    bot.send_message(message.from_user.id, "Memory Information")
    # get the memory details
    svmem = psutil.virtual_memory()
    bot.send_message(message.from_user.id, f"Total: {get_size(svmem.total)}")
    bot.send_message(message.from_user.id, f"Available: {get_size(svmem.available)}")
    bot.send_message(message.from_user.id, f"Used: {get_size(svmem.used)}")
    bot.send_message(message.from_user.id, f"Percentage: {svmem.percent}%")

    bot.send_message(message.from_user.id, "SWAP")
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    bot.send_message(message.from_user.id, f"Total: {get_size(swap.total)}")
    bot.send_message(message.from_user.id, f"Free: {get_size(swap.free)}")
    bot.send_message(message.from_user.id, f"Used: {get_size(swap.used)}")
    bot.send_message(message.from_user.id, f"Percentage: {swap.percent}%")

    # Disk Information
    bot.send_message(message.from_user.id, "Disk Information")
    bot.send_message(message.from_user.id, "Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        bot.send_message(message.from_user.id, f"=== Device: {partition.device} ===")
        bot.send_message(message.from_user.id, f"  Mountpoint: {partition.mountpoint}")
        bot.send_message(message.from_user.id, f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        bot.send_message(message.from_user.id, f"  Total Size: {get_size(partition_usage.total)}")
        bot.send_message(message.from_user.id, f"  Used: {get_size(partition_usage.used)}")
        bot.send_message(message.from_user.id, f"  Free: {get_size(partition_usage.free)}")
        bot.send_message(message.from_user.id, f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    bot.send_message(message.from_user.id, f"Total read: {get_size(disk_io.read_bytes)}")
    bot.send_message(message.from_user.id, f"Total write: {get_size(disk_io.write_bytes)}")

    # Network information
    bot.send_message(message.from_user.id, "Network Information")
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            bot.send_message(message.from_user.id, f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                bot.send_message(message.from_user.id, f"  IP Address: {address.address}")
                bot.send_message(message.from_user.id, f"  Netmask: {address.netmask}")
                bot.send_message(message.from_user.id, f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                bot.send_message(message.from_user.id, f"  MAC Address: {address.address}")
                bot.send_message(message.from_user.id, f"  Netmask: {address.netmask}")
                bot.send_message(message.from_user.id, f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    bot.send_message(message.from_user.id, f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    bot.send_message(message.from_user.id, f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


@bot.message_handler(commands=['check_or_add_phone'])
def check_or_add_phone(message):
    bot.send_message(message.from_user.id, "Введи номер телефона для проверки")
    bot.register_next_step_handler(message, on_check_or_add_phone)


def on_add_phone(message):
    new_phone = Phone(phone=saved_phone)
    db.add(new_phone)

    # Commit the transaction
    db.commit()

    # Refresh the new_user instance to get the latest data from the database
    db.refresh(new_phone)

    # Print the new user ID
    print(new_phone.id)

    # Close the session
    db.close()

    bot.send_message(message.from_user.id, 'Готово ✅')


@bot.message_handler(commands=['decide_to_add'])
def on_decide_to_add(message):
    if message.text.strip() == 'yes' or message.text.strip() == 'да':
        on_add_phone(message)
    else:
        bot.send_message(message.from_user.id, 'Нууу, нет, так нет')


@bot.message_handler(commands=['on_check_or_add_phone'])
def on_check_or_add_phone(message):
    match = re.fullmatch(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                         message.text.strip())
    if not match:
        bot.send_message(message.from_user.id, "Введи корректный номер телефона")
        bot.register_next_step_handler(message, on_check_or_add_phone)
        return

    text = message.text.strip()

    selected_phone = phones.select().where(phones.c.phone == text)
    result = connection.execute(selected_phone)

    if result.first() is not None:
        bot.send_message(message.from_user.id, 'Данный номер уже присутствует в БД 😀')
    else:
        bot.send_message(message.from_user.id, 'Данный номер отсутствует в БД ☹️. Хочешь добавить его туда?')
        global saved_phone
        saved_phone = text
        bot.register_next_step_handler(message, on_decide_to_add)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if (message.text != '/check_phone') or (message.text != '/check_email'):
        bot.send_message(message.from_user.id,
                         f"Данная команда недоступна. Используй {'/check_phone'}, {'/check_email'}, {'/check_password'}, {'/check_specs'} или {'/check_or_add_phone'}")


bot.infinity_polling()
