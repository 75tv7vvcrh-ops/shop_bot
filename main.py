import asyncio
import logging

from bot import bot, dp
from services.database import init_db, close_pool

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

    logging.info("Инициализация базы данных...")
    await init_db()

    logging.info("Запуск бота...")

    try:
        await dp.start_polling(bot)

    finally:
        logging.info("Закрытие соединений PostgreSQL...")
        await close_pool()

        await bot.session.close()

        logging.info("Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass