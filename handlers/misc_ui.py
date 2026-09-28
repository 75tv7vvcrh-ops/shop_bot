from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import router
from keyboards.keyboards import delete_keyboard_builder, redact_keyboard_builder, back_keyboard_builder, keyboard


@router.message(Command(commands=["inline"]))
async def inline_command(message: Message):
    inline_keyboard_builder = InlineKeyboardBuilder()
    inline_keyboard_builder.button(text="👤 Профиль", callback_data="inline:profile")
    inline_keyboard_builder.button(text="⚙️ Настройки", callback_data="inline:settings")
    inline_keyboard_builder.button(text="❌ Закрыть", callback_data="inline:close")
    inline_keyboard_builder.adjust(1)
    await message.answer("📋 Выбери действие:\n", reply_markup=inline_keyboard_builder.as_markup())


@router.callback_query(F.data.startswith("inline:"))
async def inline_callback(callback_query: CallbackQuery):
    action = callback_query.data.split(":")[1]
    if action == "profile":
        await callback_query.message.answer("👤 Твой профиль")
    elif action == "settings":
        await callback_query.message.answer("⚙️ Настройки")
    elif action == "close":
        await callback_query.message.delete()
    await callback_query.answer()


@router.message(Command(commands=["delete"]))
async def delete_command(message: Message):
    await message.answer("🗑 Это сообщение можно удалить\n", reply_markup=delete_keyboard_builder.as_markup())


@router.callback_query(F.data == "delete")
async def delete_callback(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer()


@router.message(Command(commands=["redact"]))
async def redact_command(message: Message):
    await message.answer("✏️ Отредактируй сообщение\n", reply_markup=redact_keyboard_builder.as_markup())


@router.callback_query(F.data == "redact")
async def redact_callback(callback_query: CallbackQuery):
    await callback_query.message.edit_text("✅ Сообщение изменено!")
    await callback_query.message.edit_reply_markup(reply_markup=back_keyboard_builder.as_markup())
    await callback_query.answer()


@router.callback_query(F.data == "back_to_menu")
async def redact_callback_back(callback_query: CallbackQuery):
    await callback_query.message.edit_text("⬅️ Вы вернулись в главное меню.", reply_markup=keyboard)
    await callback_query.answer()