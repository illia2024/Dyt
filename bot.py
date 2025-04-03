from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import logging
import psutil
import time
import asyncio

TOKEN = "7668112308:AAE26s1lNmpDNrT4lXOJQKUnup4oDKpeEyk"  # Вставте свій токен тут
ADMIN_ID = 1428115542  # Замініть на свій ID

# Настройка логування
logging.basicConfig(level=logging.INFO)

# Створення об'єктів
application = Application.builder().token(TOKEN).build()

# Перемінні для статистики
start_time = time.time()
sent_messages = 0
users = set()

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

    await update.message.reply(text)

def main():
    # Додавання обробників
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE, forward_to_admin))
    application.add_handler(CommandHandler("info_bot", bot_info))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
