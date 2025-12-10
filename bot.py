import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from handlers import router

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(router)

# Основная функция
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🔁 Старт / Перезапуск"),
        types.BotCommand(command="restart", description="🔄 Перезапуск"),
        types.BotCommand(command="settings", description="⚙️ Настройки"),
        types.BotCommand(command="stats", description="📊 Статистика"),
        types.BotCommand(command="about", description="ℹ️ О нас"),
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())