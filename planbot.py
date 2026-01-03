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
               plan TEXT,
               completed_plans INTEGER DEFAULT 0,
               username TEXT
)''')
connection.commit()

@bot.message_handler(commands=['start'])
def hello_message(message):
    print(message)
    id = message.from_user.id
    username = '@' + message.from_user.username
    cursor.execute('''INSERT INTO Users(user_id, username) VALUES (?, ?)''', (id, username))
    connection.commit()
    bot.send_message(message.chat.id, "Привет, я бот-планировщик дел. Чтобы получить информацию по командам, используйте /help")
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "/help - Выводит список команд\n/create_plan <Пункты плана через запятую с пробелом> - Создает новый план\n/add_task <Пункт> - Добавляет пункт в план\n/complete_task <Пункт> - Засчитывает пункт как выполненный\n/delete_task <Пункт> Удаляет пункт из плана\n/print_plan - Выводит план\n/plans - Выводит кол-во выполненных вами планов\n/top10 - Выводит топ-10 по кол-ву выполненных планов")
@bot.message_handler(commands=['print_plan'])
def print_plan(message):
     cursor.execute('''SELECT DISTINCT completed_tasks, active_tasks FROM Users WHERE user_id = ?''', (message.from_user.id,))
     executed = cursor.fetchone()
     text = 'Невыполнено:\n'
     if executed[1] is None:
          active_tasks = ""
     else:
        active_tasks = '- ' + '\n- '.join(executed[1].split(', '))
     text += active_tasks + '\n'
     text += 'Выполнено:\n'
     if executed[0] is None:
        completed_tasks = ""
     else:
        completed_tasks = '- ' + '\n- '.join(executed[0].split(', '))
     text += completed_tasks + '\n'
     bot.send_message(message.chat.id, text)
@bot.message_handler(commands=['create_plan'])
def create_plan(message):
    tasks = message.text[13:]
    cursor.execute('''SELECT DISTINCT active_tasks, plan FROM Users WHERE user_id = ?''', (message.from_user.id,))
    executed = cursor.fetchone()
    if not executed[0] and executed[1]:
        cursor.execute('''UPDATE Users SET completed_tasks = NULL, active_tasks = ?, plan = ?, completed_plans = completed_plans + 1 WHERE user_id = ?''', (tasks, tasks, message.from_user.id))
    else:
        cursor.execute('''UPDATE Users SET completed_tasks = NULL, active_tasks = ?, plan = ?, completed_plans = completed_plans WHERE user_id = ?''', (tasks, tasks, message.from_user.id))
    connection.commit()
    bot.send_message(message.chat.id, "План успешно создан")
    print_plan(message)
@bot.message_handler(commands=["add_task"])
def add_task(message):
    cursor.execute('''SELECT DISTINCT active_tasks, plan FROM Users WHERE user_id = ?''', (message.from_user.id,))
    executed = cursor.fetchone()
    try:
        plan = executed[1].split(', ')
        if executed[0] is None:
            active_tasks = []
        else:
            active_tasks = executed[0].split(', ')
        text = message.text[10:]
        plan.append(text)
        active_tasks.append(text)
        cursor.execute('''UPDATE Users SET active_tasks = ?, plan = ? WHERE user_id = ?''', (', '.join(active_tasks), ', '.join(plan), message.from_user.id))
        connection.commit()
        bot.send_message(message.chat.id, "Пункт успешно добавлен")
    except AttributeError:
        bot.send_message(message.chat.id, "План не создан")
    print_plan(message)
@bot.message_handler(commands=['complete_task'])
def complete_task(message):
    cursor.execute('''SELECT DISTINCT completed_tasks, active_tasks FROM Users WHERE user_id = ?''', (message.from_user.id,))
    executed = cursor.fetchone()
    if executed[0] is None:
        completed_tasks = []
    else:
        completed_tasks = executed[0].split(', ')
    if executed[1] is None:
        active_tasks = []
    else:
        active_tasks = executed[1].split(', ')
    task = message.text[15:]
    completed_tasks.append(task)
    active_tasks.remove(task)
    cursor.execute('''UPDATE Users SET completed_tasks = ?, active_tasks = ? WHERE user_id = ?''', (', '.join(completed_tasks), ', '.join(active_tasks), message.from_user.id))
    connection.commit()
    bot.send_message(message.chat.id, "Пункт успешно зачтен")
    print_plan(message)
@bot.message_handler(commands=['delete_task'])
def delete_task(message):
    cursor.execute('''SELECT DISCTINCT plan, active_tasks FROM Users WHERE user_id = ?''', (message.from_user.id,))
    executed = cursor.fetchone()
    if executed[0] is None:
        plan = []
    else:
        plan = executed[0].split(', ')
    if executed[1] is None:
        active_tasks = []
    else:
        active_tasks = executed[1].split(', ')
    task = message.text[13:]
    plan.remove(task)
    active_tasks.remove(task)
    cursor.execute('''UPDATE Users SET plan = ?, active_tasks = ? WHERE user_id = ?''', (', '.join(plan), ', '.join(active_tasks), message.from_user.id))
    connection.commit()
    bot.send_message(message.chat.id, "Пункт успешно удален")
    print_plan(message)
@bot.message_handler(commands=['plans'])
def plans(message):
    cursor.execute('''SELECT DISCTINCT completed_plans FROM Users WHERE user_id = ?''', (message.from_user.id,))
    cnt = cursor.fetchone()[0]
    bot.send_message(message.chat.id, f"Кол-во выполненных планов: {cnt}")
@bot.message_handler(commands=['top10'])
def top10(message):
    cursor.execute('''SELECT DISTINCT username, completed_plans FROM Users ORDER BY completed_plans DESC LIMIT 10''')
    executed = cursor.fetchall()
    print(executed)
try:
    bot.infinity_polling()
except KeyboardInterrupt:
    pass
finally:
        connection.close()