import logging
import psutil
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "7668112308:AAE26s1lNmpDNrT4lXOJQKUnup4oDKpeEyk"  
ADMIN_ID = 1428115542  # ID адміністратора має бути цілим числом, без лапок

# Налаштування логування
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Змінні для відстеження часу роботи та повідомлень
start_time = time.time()
sent_messages = 0
users = set()

# Функція для форматування часу роботи бота
def format_uptime(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

# Обробник команди /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    global users
    users.add(message.from_user.id)
    text = "🧬 Надішліть фото / відео / голосове, і я відправлю -----> @xxqwer_x"
    await message.answer(text)

# Обробник повідомлень із фото, відео або голосовими
@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.VOICE])
async def forward_to_admin(message: Message):
    global sent_messages
    sent_messages += 1
    await message.forward(ADMIN_ID)

# Обробник команди /info_bot (доступ тільки для адміністратора)
@dp.message_handler(commands=['info_bot'])
async def bot_info(message: Message):
    if message.from_user.id != ADMIN_ID:
        return  # Якщо не адмін, просто ігноруємо запит

    uptime = format_uptime(time.time() - start_time)
    memory = psutil.virtual_memory().used / (1024 ** 3)
    disk = psutil.disk_usage('/').used / (1024 ** 3)
    start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))

    text = (f"⏳ Час роботи: {uptime}\n"
            f"💾 Використання пам'яті: {memory:.2f} GB\n"
            f"💽 Використання диску: {disk:.2f} GB\n"
            f"================================\n"
            f"📶 Бот запущений: {start_time_str}\n"
            f"📨 Відправлено повідомлень: {sent_messages}\n"
            f"⌨️ Кількість користувачів: {len(users)}")

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔀 Оновити", callback_data="update_info")
    )

    await message.answer(text, reply_markup=keyboard)

# Обробник кнопки "Оновити"
@dp.callback_query_handler(lambda c: c.data == "update_info")
async def update_info(callback_query: types.CallbackQuery):
    await bot_info(callback_query.message)
    await callback_query.answer()

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
