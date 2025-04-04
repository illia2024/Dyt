from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import logging
import psutil
import time
import asyncio
import os

TOKEN = "7668112308:AAE26s1lNmpDNrT4lXOJQKUnup4oDKpeEyk"  # Вставте свій токен тут
ADMIN_ID = 1428115542  # Замініть на свій ID

# Файл для збереження часу старту
START_TIME_FILE = "start_time.txt"

# Настройка логування
logging.basicConfig(level=logging.INFO)

# Створення об'єктів
application = Application.builder().token(TOKEN).build()

# Перемінні для статистики
sent_messages = 0
users = set()

# Функція для збереження часу старту
def save_start_time():
    with open(START_TIME_FILE, 'w') as f:
        f.write(str(time.time()))

# Функція для отримання часу старту
def get_start_time():
    if os.path.exists(START_TIME_FILE):
        with open(START_TIME_FILE, 'r') as f:
            return float(f.read())
    else:
        save_start_time()  # Якщо файл не існує, створюємо новий час
        return time.time()

start_time = get_start_time()

def format_uptime(seconds):
    """Форматування часу роботи бота."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

async def start(update: Update, context):
    """Привітальне повідомлення при старті."""
    global users
    users.add(update.message.from_user.id)
    text = "🧪 Надішліть фото / відео / голосове, і я відправлю -----> @xxqwer_x"
    await update.message.answer(text)

async def forward_to_admin(update: Update, context):
    """Пересилання медіафайлів адміну."""
    global sent_messages
    sent_messages += 1
    await update.message.forward(chat_id=ADMIN_ID)

async def bot_info(update: Update, context):
    """Виведення інформації про бота (тільки для адміністраторів)."""
    if update.message.from_user.id != ADMIN_ID:
        return

    uptime = format_uptime(time.time() - start_time)
    memory = psutil.virtual_memory().used / (1024 ** 3)
    disk = psutil.disk_usage('/').used / (1024 ** 3)
    start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

    text = (f"⏳ Час роботи: {uptime}\n"
            f"💾 Пам'ять: {memory:.2f} GB\n"
            f"💽 Диск: {disk:.2f} GB\n"
            f"================================\n"
            f"📶 Бот запущений: {start_time_str}\n"
            f"📨 Відправлено повідомлень: {sent_messages}\n"
            f"⌨️ Кількість користувачів: {len(users)}")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def main():
    # Додавання обробників
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE, forward_to_admin))
    application.add_handler(CommandHandler("info_bot", bot_info))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
