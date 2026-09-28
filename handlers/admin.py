from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID
from middlewares.ban import banned_users
from services.database import get_connection

router = Router()


class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    stock = State()
    category = State()
    photo = State()


# 👑 Панель администратора с кнопками управления статусами
@router.message(Command(commands=["admin"]))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав администратора.")
        return

    conn = await get_connection()
    try:
        # Извлекаем только активные заказы (не отмененные и не выполненные)
        orders = await conn.fetch(
        """
            SELECT id, user_id, total_amount, status 
            FROM orders 
            WHERE status NOT IN ('✅ Выполнен', '❌ Отменен') 
            ORDER BY id DESC 
            LIMIT 10
         """
        )
        
        if not orders:
            await message.answer("👑 <b>Панель админа</b>\n\nЗаказов пока нет.\n\n➕ Добавить товар: /add_product", parse_mode="HTML")
            return

        await message.answer("👑 <b>Панель администратора (Последние 5 заказов):</b>", parse_mode="HTML")
        
        for o in orders:
            text = (
                f"📦 <b>Заказ #{o['id']}</b>\n"
                f"👤 User ID: <code>{o['user_id']}</code>\n"
                f"💰 Сумма: {o['total_amount']} ₽\n"
                f"📌 Статус: <b>{o['status']}</b>"
            )
            
            # Клавиатура смены статуса
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⏳ В обработку", callback_data=f"status_{o['id']}_PROCESSING"),
                    InlineKeyboardButton(text="✅ Выполнен", callback_data=f"status_{o['id']}_DONE")
                ],
                [
                    InlineKeyboardButton(text="❌ Отменить", callback_data=f"status_{o['id']}_CANCELLED")
                ]
            ])
            
            await message.answer(text, reply_markup=kb, parse_mode="HTML")
            
    finally:
        await conn.close()


# 🔄 Обработчик смены статуса заказа
@router.callback_query(F.data.startswith("status_"))
async def change_order_status(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    _, order_id, new_status = callback.data.split("_")
    order_id = int(order_id)

    status_labels = {
        "PROCESSING": "⏳ В обработке",
        "DONE": "✅ Выполнен",
        "CANCELLED": "❌ Отменен"
    }
    
    status_text = status_labels.get(new_status, new_status)

    conn = await get_connection()
    try:
        # Обновляем статус в БД и получаем user_id заказчика
        order = await conn.fetchrow(
            "UPDATE orders SET status = $1 WHERE id = $2 RETURNING user_id",
            status_text, order_id
        )

        if order:
            user_id = order["user_id"]
            await callback.answer(f"Статус заказа #{order_id} изменен на {status_text}")
            await callback.message.edit_text(
                f"📦 <b>Заказ #{order_id}</b>\n"
                f"👤 User ID: <code>{user_id}</code>\n"
                f"📌 Обновленный статус: <b>{status_text}</b>",
                parse_mode="HTML"
            )

            # Уведомляем клиента об изменении статуса
            try:
                await callback.bot.send_message(
                    chat_id=user_id,
                    text=f"🔔 <b>Статус вашего заказа #{order_id} изменен:</b> {status_text}",
                    parse_mode="HTML"
                )
            except Exception:
                pass  # Если пользователь заблокировал бота
    finally:
        await conn.close()


# --- Бан / Разбан ---

@router.message(Command(commands=["ban"]))
async def ban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("Использование: <code>/ban &lt;user_id&gt; [причина]</code>", parse_mode="HTML")
        return

    try:
        user_id = int(args[1])
        reason = args[2] if len(args) > 2 else "Не указана"
        banned_users[user_id] = reason
        await message.answer(f"⛔ Пользователь <code>{user_id}</code> заблокирован. Причина: {reason}", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.")


@router.message(Command(commands=["unban"]))
async def unban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: <code>/unban &lt;user_id&gt;</code>", parse_mode="HTML")
        return

    try:
        user_id = int(args[1])
        if user_id in banned_users:
            del banned_users[user_id]
            await message.answer(f"✅ Пользователь <code>{user_id}</code> разблокирован.", parse_mode="HTML")
        else:
            await message.answer("Пользователь не найден в списке забаненных.")
    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.")


# --- FSM Хэндлеры добавления товара ---

@router.message(Command(commands=["add_product"]))
async def start_add_product(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(AddProductFSM.name)
    await message.answer("📦 Напишите <b>название товара</b>:", parse_mode="HTML")


@router.message(AddProductFSM.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProductFSM.description)
    await message.answer("📝 Введите <b>описание товара</b>:", parse_mode="HTML")


@router.message(AddProductFSM.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProductFSM.price)
    await message.answer("💰 Введите <b>цену товара</b> (числом):", parse_mode="HTML")


@router.message(AddProductFSM.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price_val = float(message.text.replace(",", "."))
        if price_val <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Ошибка! Введите корректное положительное число для цены.")
        return

    await state.update_data(price=price_val)
    await state.set_state(AddProductFSM.stock)
    await message.answer("🔢 Введите <b>количество товара на складе</b> (шт):", parse_mode="HTML")


@router.message(AddProductFSM.stock)
async def process_stock(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Ошибка! Количество должно быть целым числом.")
        return

    await state.update_data(stock=int(message.text))
    await state.set_state(AddProductFSM.category)
    await message.answer("🏷 Введите <b>категорию товара</b> (например: <i>Обувь</i>, <i>Одежда</i>):", parse_mode="HTML")


@router.message(AddProductFSM.category)
async def process_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddProductFSM.photo)
    await message.answer("📸 Отправьте <b>изображение товара</b> (как фото):", parse_mode="HTML")


@router.message(AddProductFSM.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()

    conn = await get_connection()
    try:
        await conn.execute(
            """
            INSERT INTO products (name, description, price, stock, category, image_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            data["name"],
            data["description"],
            data["price"],
            data["stock"],
            data["category"],
            photo_id
        )
    finally:
        await conn.close()

    await state.clear()

    await message.answer_photo(
        photo=photo_id,
        caption=f"✅ <b>Товар успешно добавлен в базу!</b>\n\n"
                f"📌 <b>Название:</b> {data['name']}\n"
                f"📝 <b>Описание:</b> {data['description']}\n"
                f"💰 <b>Цена:</b> {data['price']} ₽\n"
                f"🔢 <b>На складе:</b> {data['stock']} шт.\n"
                f"🏷 <b>Категория:</b> {data['category']}",
        parse_mode="HTML"
    )