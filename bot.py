from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from middlewares.ban import BanMiddleware

from handlers.errors import router as errors_router
from handlers.start import router as start_router
from handlers.catalog import router as catalog_router
from handlers.cart import router as cart_router
from handlers.registration import router as registration_router
from handlers.admin import router as admin_router
from handlers.orders import router as orders_router  # 1. Импортируем новый роутер

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# Регистрируем BanMiddleware глобально для сообщений и колбэков
dp.message.outer_middleware(BanMiddleware())
dp.callback_query.outer_middleware(BanMiddleware())

# Подключаем роутеры
dp.include_router(start_router)
dp.include_router(catalog_router)
dp.include_router(cart_router)
dp.include_router(registration_router)
dp.include_router(admin_router)
dp.include_router(orders_router)  # 2. Подключаем роутер заказов
dp.include_router(errors_router)