from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from callbacks.callback_data import ProductCallback
from keyboards.keyboards import (
    get_products_inline_keyboard,
    get_product_detail_keyboard
)
from services.database import get_connection


router = Router()


@router.message(F.text == "🛍 Каталог")
async def show_catalog(message: Message):
    conn = await get_connection()

    try:
        products = await conn.fetch(
            """
            SELECT id, name, price
            FROM products
            WHERE stock > 0
            ORDER BY id
            """
        )

        if not products:
            await message.answer(
                "❌ Каталог товаров сейчас пуст."
            )
            return

        products_list = [dict(product) for product in products]

        keyboard = get_products_inline_keyboard(
            products_list
        )

        await message.answer(
            "🛍 <b>Выберите товар из каталога:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    finally:
        await conn.close()


@router.callback_query(ProductCallback.filter())
async def show_product_detail(
    callback: CallbackQuery,
    callback_data: ProductCallback
):
    product_id = callback_data.product_id

    conn = await get_connection()

    try:
        product = await conn.fetchrow(
            """
            SELECT
                id,
                name,
                description,
                price,
                stock,
                image_id
            FROM products
            WHERE id = $1
            """,
            product_id
        )

        if not product:
            await callback.answer(
                "❌ Товар не найден.",
                show_alert=True
            )
            return

        text = (
            f"📦 <b>{product['name']}</b>\n\n"
        )

        if product["description"]:
            text += (
                f"📝 {product['description']}\n\n"
            )

        text += (
            f"💰 Цена: <b>{product['price']:,.0f} ₽</b>\n".replace(",", " "),
            f"📊 В наличии: {product['stock']} шт."
        )

        keyboard = get_product_detail_keyboard(
            product_id
        )

        # Если у товара есть фотография —
        # отправляем фото
        if product["image_id"]:
            try:
                await callback.message.delete()

                await callback.message.answer_photo(
                    photo=product["image_id"],
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

            except Exception:
                await callback.message.answer(
                    text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

        else:
            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    finally:
        await conn.close()

    await callback.answer()


@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog_handler(
    callback: CallbackQuery
):
    conn = await get_connection()

    try:
        products = await conn.fetch(
            """
            SELECT id, name, price
            FROM products
            WHERE stock > 0
            ORDER BY id
            """
        )

        if not products:
            await callback.message.edit_text(
                "❌ Каталог товаров сейчас пуст."
            )
            await callback.answer()
            return

        products_list = [dict(product) for product in products]

        keyboard = get_products_inline_keyboard(
            products_list
        )

        # Если предыдущее сообщение было фото,
        # удаляем его и отправляем обычный каталог.
        try:
            await callback.message.delete()

            await callback.message.answer(
                "🛍 <b>Выберите товар из каталога:</b>",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        except Exception:
            await callback.message.edit_text(
                "🛍 <b>Выберите товар из каталога:</b>",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    finally:
        await conn.close()

    await callback.answer()