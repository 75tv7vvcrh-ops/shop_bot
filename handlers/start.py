import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommandScopeChat

from config import ADMIN_ID
from keyboards.keyboards import keyboard, user_commands, admin_commands
from services.database import add_user_if_not_exists

router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: Message, command: CommandObject):
    logging.info(f"START | id={message.from_user.id} | username={message.from_user.username} | args={command.args}")
    
    source = command.args if command.args else "direct"
    await add_user_if_not_exists(user_id=message.from_user.id, source=source)

    if message.from_user.id == ADMIN_ID:
        await message.bot.set_my_commands(commands=admin_commands, scope=BotCommandScopeChat(chat_id=message.from_user.id))
    else:
        await message.bot.set_my_commands(commands=user_commands, scope=BotCommandScopeChat(chat_id=message.from_user.id))

    await message.answer(
        f"Добро пожаловать в наш магазин!\n"
        f"Имя: {message.from_user.first_name}\n"
        f"ID: {message.from_user.id}",
        reply_markup=keyboard
    )

# ℹ️ Добавляем обработчик кнопки "О магазине"
@router.message(F.text.contains("О магазине"))
async def about_shop_handler(message: Message):
    about_text = (
        "🏪 <b>Добро пожаловать в наш интернет-магазин!</b>\n\n"
        "📍 <b>Адрес:</b> г. Москва, ул. Примерная, д. 10\n"
        "🕒 <b>Режим работы:</b> Ежедневно с 10:00 до 22:00\n"
        "🚚 <b>Доставка:</b> По всей России курьером и СДЭК\n"
        "📞 <b>Поддержка:</b> @admin_username\n\n"
        "Спасибо, что выбираете нас! ❤️"
    )
    await message.answer(about_text, parse_mode="HTML")