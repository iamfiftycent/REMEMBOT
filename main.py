import telebot
from bot.config import TOKEN
from datetime import datetime, date, time


DATE_FORMAT = '%d.%m.%Y'
TIME_FORMAT = '%H:%M'

bot = telebot.TeleBot(TOKEN)

reminders = []


def get_time(message, reminder_date, reminder_text):
    reminder_time = message.text
    reminder = {
        'text': reminder_text,
        'date': reminder_date,
        'time': reminder_time,
    }
    reminders.append(reminder)


def get_date(message, reminder_text):
    reminder_date = message.text
    bot.send_message(message.from_user.id, "Введи время в формате 'ЧЧ:ММ'")
    bot.register_next_step_handler(message, get_time, reminder_date, reminder_text)


def get_reminder(message):
    reminder_text = message.text
    bot.send_message(message.from_user.id, "Введи дату напоминания в формате"
                                           " 'ДД.ММ.ГГ'")
    bot.register_next_step_handler(message, get_date, reminder_text)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """Функция, принимающая сообщения пользователя."""
    if message.text in ['Привет', '/start']:
        bot.send_message(message.from_user.id, "Привет, это бот-напоминалка.\n"
                                               "Введи 'Напомни', чтобы"
                                               "ничего не забыть!\nВведи /help"
                                               " для просмотра команд.")
    elif message.text == '/help':
        # Дописать список команд
        bot.send_message(message.from_user.id, "Список доступных команд: ")
    elif message.text == 'Напомни':
        bot.send_message(message.from_user.id, "Что именно напомнить?)")
        bot.register_next_step_handler(message, get_reminder)
    else:
        bot.send_message(message.from_user.id, "Неизвестная команда, введите "
                                               "/help для просмотра списка "
                                               "команд.")


bot.polling(none_stop=True, interval=0)
