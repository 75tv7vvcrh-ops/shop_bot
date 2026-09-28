import asyncio
import logging

from bot import bot, dp
from services.database import init_db

# Подключаем хэндлеры
import handlers.start
import handlers.catalog
import handlers.cart
import handlers.registration
import handlers.admin

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    # 1. Инициализируем структуры таблиц в PostgreSQL
    logging.info("Инициализация базы данных...")
    await init_db()

    # 2. Запускаем polling бота
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())