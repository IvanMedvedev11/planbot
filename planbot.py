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
     bot.send_message(message.chat.id, "/help - Выводит список команд\n/create_plan <Пункты плана через пробел> - Создает новый план\n/add_task <Пункт> - Добавляет пункт в план\n/complete_task <Пункт> - Засчитывает пункт как выполненный\n/delete_task <Пункт> Удаляет пункт из плана")
try:
    bot.infinity_polling()
except KeyboardInterrupt:
    pass
finally:
        connection.close()