from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from callbacks.callback_data import AddCartCallback
from config import ADMIN_ID
from services.database import get_connection

router = Router()

@router.callback_query(AddCartCallback.filter())
async def add_to_cart_handler(callback: CallbackQuery, callback_data: AddCartCallback):
    product_id = callback_data.product_id
    user_id = callback.from_user.id

    conn = await get_connection()
    try:
        cart_item = await conn.fetchrow(
            "SELECT quantity FROM cart WHERE user_id = $1 AND product_id = $2",
            user_id, product_id
        )

        if cart_item:
            await conn.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE user_id = $1 AND product_id = $2",
                user_id, product_id
            )
        else:
            await conn.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES ($1, $2, 1)",
                user_id, product_id
            )

        await callback.answer("✅ Товар добавлен в корзину!", show_alert=False)
    finally:
        await conn.close()


@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    user_id = message.from_user.id
    conn = await get_connection()
    
    try:
        items = await conn.fetch("""
            SELECT p.name, p.price, c.quantity, (p.price * c.quantity) as total_price
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = $1
        """, user_id)

        if not items:
            await message.answer("🛒 Ваша корзина пуста.")
            return

        text = "🛒 <b>Ваша корзина:</b>\n\n"
        grand_total = 0
        for item in items:
            text += f"• <b>{item['name']}</b> x{item['quantity']} — {item['total_price']} ₽\n"
            grand_total += item['total_price']

        text += f"\n💰 <b>Итого к оплате:</b> {grand_total} ₽"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout")]
        ])

        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    finally:
        await conn.close()


@router.callback_query(F.data == "checkout")
async def checkout_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    conn = await get_connection()

    try:
        items = await conn.fetch("""
            SELECT p.id as product_id, p.name, p.price, c.quantity, (p.price * c.quantity) as total_price
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = $1
        """, user_id)

        if not items:
            await callback.answer("Ваша корзина пуста!", show_alert=True)
            return

        grand_total = sum(item['total_price'] for item in items)

        # 1. Создаём заказ в БД
        order_id = await conn.fetchval(
            "INSERT INTO orders (user_id, total_amount, status) VALUES ($1, $2, $3) RETURNING id",
            user_id, grand_total, "NEW"
        )

        # 2. Очищаем корзину
        await conn.execute("DELETE FROM cart WHERE user_id = $1", user_id)

        # Ответ клиенту
        await callback.message.edit_text(
            f"✅ <b>Заказ #{order_id} успешно оформлен!</b>\n\nСумма: {grand_total} ₽\nМенеджер свяжется с вами.",
            parse_mode="HTML"
        )

        # 3. Безопасная отправка уведомления админу (используем HTML для защиты от 'незакровшихся' символов)
        username = f"@{callback.from_user.username}" if callback.from_user.username else "без_юзернейма"
        order_details = "\n".join([f"• {i['name']} x{i['quantity']} ({i['total_price']}₽)" for i in items])
        
        admin_text = (
            f"🔔 <b>Новый заказ #{order_id}!</b>\n"
            f"Пользователь: ID {user_id} ({username})\n"
            f"Состав:\n{order_details}\n\n"
            f"💰 <b>Сумма:</b> {grand_total} ₽"
        )
        await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")

    finally:
        await conn.close()

    await callback.answer()