from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callback_data import (
    ProductCallback,
    AddCartCallback
)


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛍 Каталог"),
            KeyboardButton(text="🛒 Корзина")
        ],
        [
            KeyboardButton(text="📦 Мои заказы"),
            KeyboardButton(text="📝 Регистрация")
        ],
        [
            KeyboardButton(text="ℹ️ О магазине")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню..."
)


def get_products_inline_keyboard(products_list: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for product in products_list:
        builder.button(
            text=f"{product['name']} — {product['price']:,.0f}₽".replace(",", " "),
            callback_data=ProductCallback(
                product_id=product["id"]
            ).pack()
        )

    builder.adjust(1)

    return builder.as_markup()


def get_product_detail_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

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


user_commands = [
    BotCommand(
        command="start",
        description="🚀 Перезапустить бота"
    ),
    BotCommand(
        command="help",
        description="❓ Помощь и справка"
    ),
    BotCommand(
        command="orders",
        description="📦 Мои заказы"
    )
]


admin_commands = [
    BotCommand(
        command="start",
        description="🚀 Перезапустить бота"
    ),
    BotCommand(
        command="admin",
        description="👑 Панель администратора"
    ),
    BotCommand(
        command="ban",
        description="🚫 Заблокировать пользователя (/ban id причина)"
    ),
    BotCommand(
        command="unban",
        description="✅ Разблокировать пользователя (/unban id)"
    ),
    BotCommand(
        command="orders",
        description="📦 Мои заказы"
    )
]