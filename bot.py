import logging
import psutil
import time
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType

TOKEN = "7668112308:AAE26s1lNmpDNrT4lXOJQKUnup4oDKpeEyk"  # Вставь свой токен ADMIN_ID = 1428115542  # Замени на свой Telegram ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота, диспетчера и роутера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Переменные для статистики
start_time = time.time()
sent_messages = 0
users = set()

def format_uptime(seconds): """Форматирование времени работы бота.""" days = seconds // 86400 hours = (seconds % 86400) // 3600 minutes = (seconds % 3600) // 60 seconds = seconds % 60 return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

@router.message(Command("start")) async def send_welcome(message: Message): """Приветственное сообщение при старте.""" global users users.add(message.from_user.id) text = "🧪 Надішліть фото / відео / голосове, і я відправлю -----> @xxqwer_x" await message.answer(text)

@router.message(lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.VOICE]) async def forward_to_admin(message: Message): """Пересылка медиафайлов админу.""" global sent_messages sent_messages += 1 await message.forward(ADMIN_ID)

@router.message(Command("info_bot")) async def bot_info(message: Message): """Вывод информации о боте (только для админа).""" if message.from_user.id != ADMIN_ID: return

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

await message.answer(text, reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "update_info") async def update_info(callback_query: CallbackQuery): """Обновление информации о боте.""" await bot_info(callback_query.message) await callback_query.answer()

Добавляем router в диспетчер

dp.include_router(router)

Запуск бота

async def main(): await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())

