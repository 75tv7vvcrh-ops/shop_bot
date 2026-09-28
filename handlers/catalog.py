from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.keyboards import get_products_inline_keyboard, get_product_detail_keyboard
from services.database import get_connection

router = Router()

@router.message(F.text == "🛍 Каталог")
async def show_catalog(message: Message):
    """Выводит список всех товаров из базы данных PostgreSQL."""
    conn = await get_connection()
    try:
        # Запрашиваем товары из таблицы products
        products = await conn.fetch("SELECT id, name, price FROM products WHERE stock > 0 ORDER BY id")
        
        if not products:
            await message.answer("❌ Каталог товаров сейчас пуст.")
            return

        # Преобразуем формат asyncpg Record в список словарей
        products_list = [dict(p) for p in products]
        
        keyboard = get_products_inline_keyboard(products_list)
        await message.answer("🛍 **Выберите товар из каталога:**", reply_markup=keyboard, parse_mode="Markdown")
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback: CallbackQuery):
    """Показывает карточку конкретного товара при нажатии на его инлайн-кнопку."""
    product_id = int(callback.data.split(":")[1])
    conn = await get_connection()
    
    try:
        product = await conn.fetchrow("SELECT id, name, price, stock FROM products WHERE id = $1", product_id)
        
        if not product:
            await callback.answer("❌ Товар не найден.", show_alert=True)
            return

        text = (
            f"📦 **{product['name']}**\n\n"
            f"💰 Цена: **{product['price']} ₽**\n"
            f"📊 В наличии: {product['stock']} шт."
        )
        
        keyboard = get_product_detail_keyboard(product_id)
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    finally:
        await conn.close()
    
    await callback.answer()


@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog_handler(callback: CallbackQuery):
    """Возвращает пользователя к списку товаров при нажатии 'Назад'."""
    conn = await get_connection()
    try:
        products = await conn.fetch("SELECT id, name, price FROM products WHERE stock > 0 ORDER BY id")
        products_list = [dict(p) for p in products]
        keyboard = get_products_inline_keyboard(products_list)
        
        await callback.message.edit_text("🛍 **Выберите товар из каталога:**", reply_markup=keyboard, parse_mode="Markdown")
    finally:
        await conn.close()
    
    await callback.answer()