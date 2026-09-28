from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram import F

from bot import router
from keyboards.keyboards import menu_keyboard


@router.message(Command(commands=["user"]))
async def user_command(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(
            "❌ Пожалуйста, укажи ID пользователя.\nПример: /user 123456789"
        )
        return
    try:
        user_id = int(command.args)
        await message.answer(f"ℹ️ Информация о пользователе:\nID: {user_id}")
    except ValueError:
        await message.answer("❌ Пожалуйста, укажи корректный ID пользователя (число).")


@router.message(Command(commands=["test"]))
async def test_command(message: Message, role: str):
    if role == "admin":
        await message.answer("👑 Ты администратор!")
    else:
        await message.answer("👤 Ты обычный пользователь.")


@router.message(Command(commands=["menu"]))
async def menu_command(message: Message):
    await message.answer("Добро пожаловать!!!", reply_markup=menu_keyboard)


@router.message(F.text == "⚙️ Настройки")
async def settings_handler(message: Message):
    await message.answer("⚙️ Настройки пользователя")