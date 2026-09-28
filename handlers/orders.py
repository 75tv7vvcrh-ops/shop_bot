from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from services.database import get_connection

router = Router()

@router.message(Command("orders"))
@router.message(F.text == "📦 Мои заказы")
async def show_user_orders(message: Message):
    user_id = message.from_user.id
    conn = await get_connection()
    try:
        orders = await conn.fetch(
            "SELECT id, total_amount, status FROM orders WHERE user_id = $1 ORDER BY id DESC LIMIT 10",
            user_id
        )

        if not orders:
            await message.answer("📦 У вас пока нет оформленных заказов.")
            return

        text = "📦 <b>История ваших заказов:</b>\n\n"
        for o in orders:
            text += (
                f"🔹 <b>Заказ #{o['id']}</b> — {o['total_amount']} ₽\n"
                f"Статус: <b>{o['status']}</b>\n"
                f"----------------------------------\n"
            )

        await message.answer(text, parse_mode="HTML")
    finally:
        await conn.close()