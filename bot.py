import os
import psutil
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Токен бота
TOKEN = '7804222340:AAHANSSZXr7qRqHTJCjV1LvbnbnPtw-DPME'

# ID адміністратора (заміни на свій ID)
ADMIN_ID = '1428115542'

# Підключення до бази даних
def create_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_seen TEXT,
                        messages_sent INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bot_info (
                        id INTEGER PRIMARY KEY,
                        uptime TEXT)''')
    conn.commit()
    conn.close()

create_db()

# Функція для отримання даних користувача
def get_user_data(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

# Функція для оновлення даних користувача
def update_user_data(user_id, username):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    user_data = get_user_data(user_id)
    if user_data:
        cursor.execute('UPDATE users SET messages_sent = messages_sent + 1 WHERE user_id = ?', (user_id,))
    else:
        cursor.execute('INSERT INTO users (user_id, username, first_seen, messages_sent) VALUES (?, ?, ?, ?)', 
                       (user_id, username, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))
    conn.commit()
    conn.close()

# Функція для отримання аптайму бота
def get_bot_uptime():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT uptime FROM bot_info WHERE id = 1')
    uptime = cursor.fetchone()
    conn.close()
    return uptime[0] if uptime else '0 days 00:00:00'

# Функція для оновлення аптайму
def update_bot_uptime():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    uptime = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
    cursor.execute('REPLACE INTO bot_info (id, uptime) VALUES (1, ?)', (uptime,))
    conn.commit()
    conn.close()

# Команда /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    update_user_data(user_id, username)
    update.message.reply_text("🔥Привіт, я бот для зворотнього зв'язку, підтримую лише Відео, фото")
    update.message.reply_text("Ваші дані збережено!")

# Адмін панель
def admin_panel(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("🔶Вст. Фото", callback_data='set_photo')],
        [InlineKeyboardButton("📨Розсилка", callback_data='send_broadcast')],
        [InlineKeyboardButton("🔀Інфо", callback_data='user_info')],
        [InlineKeyboardButton("♨️БОТ", callback_data='bot_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🔧 Адмін панель", reply_markup=reply_markup)

# Обробка кнопок адмін панелі
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'set_photo':
        query.edit_message_text(text="🔶Вставте фото, яке буде надсилатись після старту.")
    elif query.data == 'send_broadcast':
        query.edit_message_text(text="📨Введіть текст чи надішліть фото/відео для розсилки всім користувачам.")
    elif query.data == 'user_info':
        query.edit_message_text(text="🔀Введіть юзернейм користувача або його ID.")
    elif query.data == 'bot_info':
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        uptime = get_bot_uptime()
        
        bot_info = f"""
        💾 Пам'ять: {memory_usage}%
        💽 Диск: {disk_usage}%
        ☮️ Аптайм: {uptime}
        """
        query.edit_message_text(text=bot_info)

# Розсилка повідомлення
def send_broadcast(update: Update, context: CallbackContext) -> None:
    text = update.message.text.split("\n", 1)[1] if update.message.text else ""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    for user in users:
        context.bot.send_message(user[0], text)
    conn.close()

# Обробка фото
def handle_photo(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    update_user_data(user_id, update.message.from_user.username)
    # Зберігаємо фото для подальшого використання або надсилаємо адміну
    photo_file = update.message.photo[-1].get_file()
    context.bot.send_photo(ADMIN_ID, photo_file.file_id)

# Обробка відео
def handle_video(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    update_user_data(user_id, update.message.from_user.username)
    video_file = update.message.video.get_file()
    context.bot.send_video(ADMIN_ID, video_file.file_id)

# Інфо про користувача
def user_info(update: Update, context: CallbackContext) -> None:
    username = update.message.text.split(' ', 1)[1]
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? OR user_id = ?', (username, username))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user_info_text = f"""
        📇 Користувач: @{user_data[1]}
        🔸 Вперше зайшов: {user_data[2]}
        🗯️ Надіслано повідомлень: {user_data[3]}
        """
        update.message.reply_text(user_info_text)
    else:
        update.message.reply_text("Користувача не знайдено.")

def main():
    # Налаштовуємо бота
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Обробники команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))

    # Обробники фото та відео
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    dispatcher.add_handler(MessageHandler(Filters.video, handle_video))

    # Обробник для кнопок адмін панелі
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Запускаємо бота
    updater.start_polling()

    # Бот працює до зупинки
    updater.idle()

if __name__ == "__main__":
    main()
