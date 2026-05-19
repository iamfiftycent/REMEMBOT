import telebot
import time
from datetime import datetime
import threading
from bot.config import TOKEN


DATE_FORMAT = '%d.%m.%Y'
TIME_FORMAT = '%H:%M'

bot = telebot.TeleBot(TOKEN)

reminders = []


class Cancel(Exception):
    pass


def get_time(message, reminder_date, reminder_text):
    try:
        if message.text in ['Отмена', '/back', '/help', 'Назад']:
            raise Cancel

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


def get_date(message, reminder_text):
    try:
        if message.text in ['Отмена', '/back', '/help', 'Назад']:
            raise Cancel

        reminder_date = datetime.strptime(message.text, DATE_FORMAT).date()
        bot.send_message(message.from_user.id, "Введи время в формате 'ЧЧ:ММ'")
        bot.register_next_step_handler(message, get_time,
                                       reminder_date, reminder_text)
    except ValueError:
        bot.send_message(message.from_user.id, "Введи дату напоминания в "
                                               "формате 'ДД.ММ.ГГГГ'")
        bot.register_next_step_handler(message, get_date, reminder_text)
    except Cancel:
        bot.register_next_step_handler(message, get_text_messages)


def get_reminder(message):
    reminder_text = message.text
    bot.send_message(message.from_user.id, "Введи дату напоминания в формате"
                                           " 'ДД.ММ.ГГГГ'")
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
        now = datetime.now()
        for reminder in reminders:
            if (
                now.date() == reminder['date']
                and now.time().hour == reminder['time'].hour
                and now.time().minute == reminder['time'].minute
            ):
                bot.send_message(reminder['user_id'], f"<-==-> Напоминаю! <-==->\n"
                                                      f"((-=====-=-=====-))\n"
                                                      f"{reminder['text']}\n"
                                                      f"((-=====-=-=====-))")
        time.sleep(20)


thread_check_reminder = threading.Thread(target=check_reminder)
thread_check_reminder.start()

bot.polling(none_stop=True, interval=0)
