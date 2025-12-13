import telebot
import sqlite3
from conf import TOKEN

bot = telebot.TeleBot(TOKEN)

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
               user_id INTEGER,
               completed_tasks TEXT,
               active_tasks TEXT,
               plan TEXT
)''')
connection.commit()

@bot.message_handler(commands=['start'])
def hello_message(message):
    id = message.from_user.id
    cursor.execute('''INSERT INTO Users(user_id) VALUES (?)''', (id,))
    connection.commit()
    bot.send_message(message.chat.id, "Привет, я бот-планировщик дел. Чтобы получить информацию по командам, используйте /help")
@bot.message_handler(commands=['help'])
def help_message(message):
     bot.send_message(message.chat.id, "/help - Выводит список команд\n/create_plan <Пункты плана через запятую с пробелом> - Создает новый план\n/add_task <Пункт> - Добавляет пункт в план\n/complete_task <Пункт> - Засчитывает пункт как выполненный\n/delete_task <Пункт> Удаляет пункт из плана\n/print_plan - Выводит невыполненные задания плана")
@bot.message_handler(commands=['create_plan'])
def create_plan(message):
     tasks = message.text[13:]
     cursor.execute('''UPDATE Users SET completed_tasks = NULL, active_tasks = ?, plan = ? WHERE user_id = ?''', (tasks, tasks, message.from_user.id))
     connection.commit()
     bot.send_message(message.chat.id, "План успешно создан")
@bot.message_handler(commands=["add_task"])
def add_task(message):
     cursor.execute('''SELECT DISTINCT active_tasks, plan FROM Users WHERE user_id = ?''', (message.from_user.id,))
     executed = cursor.fetchone()
     active_tasks = executed[0].split(', ')
     plan = executed[1].split(', ')
     text = message.text[10:]
     plan.append(text)
     active_tasks.append(text)
     cursor.execute('''UPDATE Users SET active_tasks = ?, plan = ? WHERE user_id = ?''', (', '.join(active_tasks), ', '.join(plan), message.from_user.id))
     connection.commit()
     bot.send_message(message.chat.id, "Пункт успешно добавлен")

@bot.message_handler(commands=['print_plan'])
def print_plan(message):
     cursor.execute('''SELECT active_tasks FROM Users WHERE user_id = ?''', (message.from_user.id,))
     plan = '\n'.join(cursor.fetchone()[0].split(', '))
     bot.send_message(message.chat.id, plan)
try:
    bot.infinity_polling()
except KeyboardInterrupt:
    pass
finally:
        connection.close()