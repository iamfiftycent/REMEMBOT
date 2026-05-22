import telebot
import time
from datetime import datetime, timedelta
import threading
from zoneinfo import ZoneInfo
from bot.config import TOKEN


krsk_tz = ZoneInfo("Asia/Krasnoyarsk")

DATE_FORMAT = '%d.%m.%Y'
TIME_FORMAT = '%H:%M'

bot = telebot.TeleBot(TOKEN)

reminders = []


class Cancel(Exception):
    pass


class NextStep(Exception):
    pass


class WrongDateTime(Exception):
    pass


def get_time(message, reminder_date, reminder_text):
    try:
        today_krsk_tz = datetime.now(krsk_tz).date()
        if reminder_date < today_krsk_tz:
            bot.send_message(message.from_user.id, "Время упущено(")
            bot.register_next_step_handler(message, get_date, reminder_text)
        if message.text in ['Отмена', '/back', '/help', 'Назад']:
            raise Cancel
        elif message.text == 'Утром':
            reminder_time = datetime.strptime('08:00', TIME_FORMAT).time()
            raise NextStep
        elif message.text == 'В обед':
            reminder_time = datetime.strptime('13:00', TIME_FORMAT).time()
            raise NextStep
        elif message.text == 'Вечером':
            reminder_time = datetime.strptime('18:00', TIME_FORMAT).time()
            raise NextStep
        reminder_time = datetime.strptime(message.text, TIME_FORMAT).time()
        reminder = {
            'user_id': message.from_user.id,
            'text': reminder_text,
            'date': reminder_date,
            'time': reminder_time,
        }
        reminders.append(reminder)
        bot.send_message(message.from_user.id, f"Создано напоминание:\n"
                                               f"{reminder_text} "
                                               f"{reminder_date.strftime('%d.%m.%Y')} "
                                               f"в {reminder_time.strftime('%H:%M')}")
    except ValueError:
        bot.send_message(message.from_user.id, "Введи время в формате 'ЧЧ:ММ'")
        bot.register_next_step_handler(message, get_time, reminder_date,
                                       reminder_text)
    except Cancel:
        bot.register_next_step_handler(message, get_text_messages)
    except NextStep:
        reminder = {
            'user_id': message.from_user.id,
            'text': reminder_text,
            'date': reminder_date,
            'time': reminder_time,
        }
        reminders.append(reminder)
        bot.send_message(message.from_user.id, f"Создано напоминание:\n"
                                               f"{reminder_text} "
                                               f"{reminder_date.strftime('%d.%m.%Y')} "
                                               f"в {reminder_time.strftime('%H:%M')}")


def get_date(message, reminder_text):
    try:
        today_krsk_tz = datetime.now(krsk_tz).date()
        if message.text in ['Отмена', '/back', '/help', 'Назад']:
            raise Cancel
        elif message.text == 'Сегодня':
            reminder_date = today_krsk_tz
            raise NextStep
        elif message.text == 'Завтра':
            reminder_date = (today_krsk_tz + timedelta(days=1)).date()
            raise NextStep
        reminder_date = datetime.strptime(message.text, DATE_FORMAT).date()
        bot.send_message(message.from_user.id, "Введи время в формате 'ЧЧ:ММ'"
                                               "или введи:\n- Утром\n- В обед"
                                               "\n-Вечером")
        bot.register_next_step_handler(message, get_time,
                                       reminder_date, reminder_text)
    except ValueError:
        bot.send_message(message.from_user.id, "Введи дату напоминания в формате"
                                               " 'ДД.ММ.ГГГГ' или введи:\n"
                                               "- Сегодня\n- Завтра")
        bot.register_next_step_handler(message, get_date, reminder_text)
    except Cancel:
        bot.register_next_step_handler(message, get_text_messages)
    except NextStep:
        bot.send_message(message.from_user.id, "Введи время в формате 'ЧЧ:ММ'"
                                               "или введи:\n- Утром\n- В обед"
                                               "\n- Вечером")
        bot.register_next_step_handler(message, get_time,
                                       reminder_date, reminder_text)


def get_reminder(message):
    reminder_text = message.text
    bot.send_message(message.from_user.id, "Введи дату напоминания в формате"
                                           " 'ДД.ММ.ГГГГ' или введи:\n"
                                           "- Сегодня\n- Завтра")
    bot.register_next_step_handler(message, get_date, reminder_text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """Функция, принимающая сообщения пользователя."""
    if message.text in ['Привет', '/start']:
        bot.send_message(message.from_user.id, "Привет, это бот-напоминалка.\n"
                                               "Введи 'Напомни', чтобы "
                                               "ничего не забыть!\nВведи /help"
                                               " для просмотра команд.")
    elif message.text == '/help':
        bot.send_message(message.from_user.id, "Список доступных команд:\n"
                                               "'Напомни' - сможешь ввести напоминание\n"
                                               "/start или 'Привет' - запуск бота\n"
                                               "/help - список команд\n"
                                               "/back или 'Отмена' или 'Назад' - отменить запись напоминания")
    elif message.text == 'Напомни':
        bot.send_message(message.from_user.id, "Что именно напомнить?)")
        bot.register_next_step_handler(message, get_reminder)
    elif message.text in ['Отмена', 'Назад', '/back']:
        bot.send_message(message.from_user.id, "Напоминание отменено!")
    else:
        bot.send_message(message.from_user.id, "Неизвестная команда, введите "
                                               "/help для просмотра списка "
                                               "команд.")


def check_reminder():
    while True:
        now = datetime.now(krsk_tz)
        for reminder in reminders:
            if (
                now.date() == reminder['date']
                and now.time().hour == reminder['time'].hour
                and now.time().minute == reminder['time'].minute
            ):
                bot.send_message(reminder['user_id'], f"<-==-> Напоминаю! <-==->\n"
                                                      f"  ========-=-========   \n"
                                                      f"{reminder['text']}\n"
                                                      f"  ========-=-========   ")
        time.sleep(20)


thread_check_reminder = threading.Thread(target=check_reminder)
thread_check_reminder.start()

bot.polling(none_stop=True, interval=0)
