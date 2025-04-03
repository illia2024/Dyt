import logging
import psutil
import time
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher

TOKEN = "7668112308:AAE26s1lNmpDNrT4lXOJQKUnup4oDKpeEyk"  # Вставьте свой токен
ADMIN_ID = 1428115542  # Замени на свой Telegram ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и обновлений
bot = Bot(token=TOKEN)
updater = Updater(bot=bot, use_context=True)
dp = updater.dispatcher

# Переменные для статистики
start_time = time.time()
sent_messages = 0
users = set()

def format_uptime(seconds):
    """Форматирование времени работы бота."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

def start(update, context):
    """Приветственное сообщение при старте."""
    global users
    users.add(update.message.from_user.id)
    text = "🧪 Надішліть фото / відео / голосове, і я відправлю -----> @xxqwer_x"
    update.message.reply_text(text)

def forward_to_admin(update, context):
    """Пересылка медиафайлов админу."""
    global sent_messages
    sent_messages += 1
    update.message.forward(chat_id=ADMIN_ID)

def bot_info(update, context):
    """Вывод информации о боте (только для админа)."""
    if update.message.from_user.id != ADMIN_ID:
        return

    uptime = format_uptime(time.time() - start_time)
    memory = psutil.virtual_memory().used / (1024 ** 3)
    disk = psutil.disk_usage('/').used / (1024 ** 3)
    start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

    text = (f"⏳ Время работы: {uptime}\n"
            f"💾 Память: {memory:.2f} GB\n"
            f"💽 Диск: {disk:.2f} GB\n"
            f"================================\n"
            f"📶 Бот запущен: {start_time_str}\n"
            f"📨 Отправлено сообщений: {sent_messages}\n"
            f"⌨️ Количество пользователей: {len(users)}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔀 Обновить", callback_data="update_info")]
    ])

    update.message.reply_text(text, reply_markup=keyboard)

def update_info(update, context):
    """Обновление информации о боте."""
    bot_info(update, context)

def button(update, context):
    """Обработка нажатия кнопки."""
    query = update.callback_query
    if query.data == "update_info":
        update_info(update, context)
    query.answer()

# Регистрируем обработчики
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.photo | Filters.video | Filters.voice, forward_to_admin))
dp.add_handler(CommandHandler("info_bot", bot_info))
dp.add_handler(CallbackQueryHandler(button))

# Запуск бота
if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
