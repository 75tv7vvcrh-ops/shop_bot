from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from callbacks.callback_data import AddCartCallback
from config import ADMIN_ID
from services.database import get_connection

router = Router()


@router.callback_query(AddCartCallback.filter())
async def add_to_cart_handler(
    callback: CallbackQuery,
    callback_data: AddCartCallback
):
    product_id = callback_data.product_id
    user_id = callback.from_user.id

    conn = await get_connection()

    try:
        product = await conn.fetchrow(
            "SELECT name, stock FROM products WHERE id = $1",
            product_id
        )

        if not product:
            await callback.answer(
                "❌ Товар не найден.",
                show_alert=True
            )
            return

        cart_item = await conn.fetchrow(
            """
            SELECT quantity
            FROM cart
            WHERE user_id = $1 AND product_id = $2
            """,
            user_id,
            product_id
        )

        current_quantity = cart_item["quantity"] if cart_item else 0

        if current_quantity >= product["stock"]:
            await callback.answer(
                f"❌ Больше нельзя добавить. В наличии: {product['stock']} шт.",
                show_alert=True
            )
            return

        if cart_item:
            await conn.execute(
                """
                UPDATE cart
                SET quantity = quantity + 1
                WHERE user_id = $1 AND product_id = $2
                """,
                user_id,
                product_id
            )
        else:
            await conn.execute(
                """
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES ($1, $2, 1)
                """,
                user_id,
                product_id
            )

        await callback.answer(
            "✅ Товар добавлен в корзину!",
            show_alert=False
        )

    finally:
        await conn.close()


@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    user_id = message.from_user.id
    conn = await get_connection()

    try:
        items = await conn.fetch(
            """
            SELECT
                p.name,
                p.price,
                p.stock,
                c.quantity,
                (p.price * c.quantity) AS total_price
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = $1
            """,
            user_id
        )

        if not items:
            await message.answer("🛒 Ваша корзина пуста.")
            return

        text = "🛒 <b>Ваша корзина:</b>\n\n"
        grand_total = 0

        for item in items:
            text += (
                f"• <b>{item['name']}</b> "
                f"x{item['quantity']} — "
                f"{item['total_price']:,.0f} ₽".replace(",", " ") + "\n"
            )
            grand_total += item["total_price"]

        text += (
            f"\n💰 <b>Итого к оплате:</b> "
            f"{grand_total:,.0f} ₽".replace(",", " ")
        )

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💳 Оформить заказ",
                        callback_data="checkout"
                    )
                ]
            ]
        )

        await message.answer(
            text,
            reply_markup=kb,
            parse_mode="HTML"
        )

    finally:
        await conn.close()


@router.callback_query(F.data == "checkout")
async def checkout_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    conn = await get_connection()

    try:
        async with conn.transaction():
            items = await conn.fetch(
                """
                SELECT
                    p.id AS product_id,
                    p.name,
                    p.price,
                    p.stock,
                    c.quantity,
                    (p.price * c.quantity) AS total_price
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = $1
                FOR UPDATE OF p
                """,
                user_id
            )

            if not items:
                await callback.answer(
                    "Ваша корзина пуста!",
                    show_alert=True
                )
                return

            # Проверяем наличие
            for item in items:
                if item["quantity"] > item["stock"]:
                    await callback.answer(
                        f"❌ Недостаточно товара «{item['name']}».\n"
                        f"В наличии: {item['stock']} шт.",
                        show_alert=True
                    )
                    return

            grand_total = sum(
                item["total_price"]
                for item in items
            )

            # 1. Создаём заказ
            order_id = await conn.fetchval(
                """
                INSERT INTO orders (user_id, total_amount, status)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                user_id,
                grand_total,
                "NEW"
            )

            # 2. Сохраняем состав заказа
            for item in items:
                await conn.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, product_name, price, quantity)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    order_id,
                    item["product_id"],
                    item["name"],
                    item["price"],
                    item["quantity"]
                )

            # 3. Уменьшаем остаток
            for item in items:
                await conn.execute(
                    """
                    UPDATE products
                    SET stock = stock - $1
                    WHERE id = $2
                    """,
                    item["quantity"],
                    item["product_id"]
                )

            # 4. Очищаем корзину
            await conn.execute(
                "DELETE FROM cart WHERE user_id = $1",
                user_id
            )

        # Транзакция успешно завершена

        await callback.message.edit_text(
            f"✅ <b>Заказ #{order_id} успешно оформлен!</b>\n\n"
            f"Сумма: {grand_total} ₽\n"
            f"Менеджер свяжется с вами.",
            parse_mode="HTML"
        )

        username = (
            f"@{callback.from_user.username}"
            if callback.from_user.username
            else "без_юзернейма"
        )

        order_details = "\n".join(
            [
                f"• {item['name']} x{item['quantity']} "
                f"({item['total_price']}₽)"
                for item in items
            ]
        )

        admin_text = (
            f"🔔 <b>Новый заказ #{order_id}!</b>\n"
            f"Пользователь: ID {user_id} ({username})\n"
            f"Состав:\n{order_details}\n\n"
            f"💰 <b>Сумма:</b> {grand_total} ₽"
        )

        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            parse_mode="HTML"
        )

    except Exception:
        await callback.answer(
            "❌ Не удалось оформить заказ. Попробуйте ещё раз.",
            show_alert=True
        )
        raise

    finally:
        await conn.close()

    await callback.answer()