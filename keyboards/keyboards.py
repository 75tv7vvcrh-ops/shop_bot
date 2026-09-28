from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.callback_data import AddCartCallback

# ============================================================
# 1. ГЛАВНАЯ REPLУ-КЛАВИАТУРА (Кнопки внизу экрана)
# ============================================================
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛍 Каталог"),
            KeyboardButton(text="🛒 Корзина")
        ],
        [
            KeyboardButton(text="📝 Регистрация"),
            KeyboardButton(text="ℹ️ О магазине")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню..."
)


# ============================================================
# 2. ИНЛАЙН-КЛАВИАТУРЫ ДЛЯ КАТАЛОГА (Динамически из БД)
# ============================================================

def get_products_inline_keyboard(products_list: list) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-кнопки для списка товаров, полученных из PostgreSQL.
    products_list — это список словарей/записей: [{'id': 1, 'name': 'iPhone', ...}, ...]
    """
    builder = InlineKeyboardBuilder()
    
    for product in products_list:
        # На кнопке пишем название товара, а в callback_data передаем его ID
        builder.button(
            text=f"{product['name']} — {product['price']}₽",
            callback_data=f"product:{product['id']}"
        )
    
    # Размещаем кнопки по 1 в ряд
    builder.adjust(1)
    return builder.as_markup()


def get_product_detail_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Генерирует кнопки для карточки конкретного товара.
    """
    builder = InlineKeyboardBuilder()
    
    # Используем фабрику колбэков AddCartCallback
    builder.button(
        text="🛒 Добавить в корзину",
        callback_data=AddCartCallback(product_id=product_id).pack()
    )
    builder.button(
        text="◀️ Назад в каталог",
        callback_data="back_to_catalog"
    )
    builder.adjust(1)
    return builder.as_markup()


# ============================================================
# 3. МЕНЮ КОМАНД (Всплывающие подсказки при вводе /)
# ============================================================

user_commands = [
    BotCommand(command="start", description="🚀 Перезапустить бота"),
    BotCommand(command="help", description="❓ Помощь и справка")
]

admin_commands = [
    BotCommand(command="start", description="🚀 Перезапустить бота"),
    BotCommand(command="admin", description="👑 Панель администратора"),
    BotCommand(command="ban", description="🚫 Заблокировать пользователя (/ban id причина)"),
    BotCommand(command="unban", description="✅ Разблокировать пользователя (/unban id)")
]