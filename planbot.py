import telebot
import sqlite3

TOKEN = "8552435655:AAGBaAy66o6FoYSEFDXolViDY0iO4gIFe_k"
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
@bot.message_handler(commands=['/help'])
def help_message(message):
     pass
try:
    bot.infinity_polling()
except KeyboardInterrupt:
    pass
finally:
        connection.close()