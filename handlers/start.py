import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommandScopeChat

from config import ADMIN_ID
from keyboards.keyboards import (
    keyboard,
    user_commands,
    admin_commands
)
from services.database import add_user_if_not_exists

router = Router()


@router.message(Command(commands=["start"]))
async def start_command(
    message: Message,
    command: CommandObject
):
    logging.info(
        "Пользователь запустил бота"
    )

    source = command.args if command.args else "direct"

    await add_user_if_not_exists(
        user_id=message.from_user.id,
        source=source
    )

    if message.from_user.id == ADMIN_ID:
        await message.bot.set_my_commands(
            commands=admin_commands,
            scope=BotCommandScopeChat(
                chat_id=message.from_user.id
            )
        )
    else:
        await message.bot.set_my_commands(
            commands=user_commands,
            scope=BotCommandScopeChat(
                chat_id=message.from_user.id
            )
        )

    await message.answer(
        "👋 <b>Добро пожаловать в магазин!</b>\n\n"
        "Здесь ты можешь:\n"
        "🛍 выбрать товар из каталога\n"
        "🛒 добавить товары в корзину\n"
        "📦 оформить заказ\n"
        "📋 посмотреть историю заказов\n\n"
        "Выбери нужный раздел в меню.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "🛍 <b>Каталог</b> — просмотр товаров\n"
        "🛒 <b>Корзина</b> — выбранные товары\n"
        "📦 <b>Мои заказы</b> — история заказов\n"
        "📝 <b>Регистрация</b> — заполнение профиля\n"
        "ℹ️ <b>О магазине</b> — информация о магазине\n\n"
        "Если возникли проблемы, обратитесь к администратору.",
        parse_mode="HTML"
    )


@router.message(F.text.contains("О магазине"))
async def about_shop_handler(message: Message):
    about_text = (
        "🏪 <b>О магазине</b>\n\n"
        "Добро пожаловать в наш магазин!\n\n"
        "🛍 Здесь можно посмотреть каталог товаров, "
        "добавить понравившиеся товары в корзину "
        "и оформить заказ прямо через бота.\n\n"
        "📦 После оформления заказа его статус "
        "можно отслеживать в разделе «📦 Мои заказы».\n\n"
        "💬 Если у вас возникли вопросы, "
        "обратитесь к администратору."
    )

    await message.answer(
        about_text,
        parse_mode="HTML"
    )