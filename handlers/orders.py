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
            """
            SELECT id, total_amount, status, created_at
            FROM orders
            WHERE user_id = $1
            ORDER BY id DESC
            LIMIT 10
            """,
            user_id
        )

        if not orders:
            await message.answer(
                "📦 У вас пока нет оформленных заказов."
            )
            return

        text = "📦 <b>История ваших заказов:</b>\n\n"

        for order in orders:
            items = await conn.fetch(
                """
                SELECT product_name, price, quantity
                FROM order_items
                WHERE order_id = $1
                ORDER BY id
                """,
                order["id"]
            )

            text += (
                f"🔹 <b>Заказ #{order['id']}</b>\n"
                f"Статус: <b>{order['status']}</b>\n"
                f"Дата: {order['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
            )

            for item in items:
                text += (
                    f"• {item['product_name']} "
                    f"x{item['quantity']} — "
                    f"{item['price'] * item['quantity']:,.0f} ₽".replace(",", " ") + "\n"
                )

            text += (
                f"\n💰 <b>Итого: "
                f"{order['total_amount']:,.0f} ₽</b>\n"
                f"━━━━━━━━━━━━━━\n\n"
            )

        await message.answer(
            text,
            parse_mode="HTML"
        )

    finally:
        await conn.close()