from decimal import Decimal, InvalidOperation

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import ADMIN_ID

from services.database import (
    get_connection,
    ban_user as db_ban_user,
    unban_user as db_unban_user
)

router = Router()


class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    stock = State()
    category = State()
    photo = State()


@router.message(Command(commands=["admin"]))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав администратора.")
        return

    conn = await get_connection()

    try:
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
            await message.answer(
                "👑 <b>Панель админа</b>\n\n"
                "Заказов пока нет.\n\n"
                "➕ Добавить товар: /add_product",
                parse_mode="HTML"
            )
            return

        await message.answer(
            "👑 <b>Панель администратора</b>",
            parse_mode="HTML"
        )

        for order in orders:
            formatted_total = (
                f"{order['total_amount']:,.0f}"
                .replace(",", " ")
            )

            text = (
                f"📦 <b>Заказ #{order['id']}</b>\n"
                f"👤 User ID: <code>{order['user_id']}</code>\n"
                f"💰 Сумма: {formatted_total} ₽\n"
                f"📌 Статус: <b>{order['status']}</b>"
            )

            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⏳ В обработку",
                            callback_data=(
                                f"status_{order['id']}_PROCESSING"
                            )
                        ),
                        InlineKeyboardButton(
                            text="✅ Выполнен",
                            callback_data=(
                                f"status_{order['id']}_DONE"
                            )
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data=(
                                f"status_{order['id']}_CANCELLED"
                            )
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

    status_text = status_labels.get(
        new_status,
        new_status
    )

    conn = await get_connection()

    try:
        order = await conn.fetchrow(
            """
            UPDATE orders
            SET status = $1
            WHERE id = $2
            RETURNING user_id
            """,
            status_text,
            order_id
        )

        if not order:
            await callback.answer(
                "❌ Заказ не найден.",
                show_alert=True
            )
            return

        user_id = order["user_id"]

        await callback.answer(
            f"Статус заказа #{order_id} изменён."
        )

        await callback.message.edit_text(
            f"📦 <b>Заказ #{order_id}</b>\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📌 Обновлённый статус: "
            f"<b>{status_text}</b>",
            parse_mode="HTML"
        )

        try:
            await callback.bot.send_message(
                chat_id=user_id,
                text=(
                    f"🔔 <b>Статус вашего заказа "
                    f"#{order_id} изменён:</b>\n"
                    f"{status_text}"
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass

    finally:
        await conn.close()


@router.message(Command(commands=["ban"]))
async def ban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(maxsplit=2)

    if len(args) < 2:
        await message.answer(
            "Использование: "
            "<code>/ban &lt;user_id&gt; [причина]</code>",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(args[1])
        reason = (
            args[2]
            if len(args) > 2
            else "Не указана"
        )

        await db_ban_user(
            user_id=user_id,
            reason=reason
        )

        await message.answer(
            f"⛔ Пользователь "
            f"<code>{user_id}</code> заблокирован.\n"
            f"Причина: {reason}",
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer(
            "❌ ID пользователя должен быть числом."
        )


@router.message(Command(commands=["unban"]))
async def unban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "Использование: "
            "<code>/unban &lt;user_id&gt;</code>",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(args[1])

        await db_unban_user(user_id)

        await message.answer(
            f"✅ Пользователь "
            f"<code>{user_id}</code> разблокирован.",
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer(
            "❌ ID пользователя должен быть числом."
        )


@router.message(Command(commands=["add_product"]))
async def start_add_product(
    message: Message,
    state: FSMContext
):
    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(
        AddProductFSM.name
    )

    await message.answer(
        "📦 Напишите <b>название товара</b>:",
        parse_mode="HTML"
    )


@router.message(AddProductFSM.name)
async def process_name(
    message: Message,
    state: FSMContext
):
    name = message.text.strip()

    if not name:
        await message.answer(
            "❌ Название товара не может быть пустым."
        )
        return

    await state.update_data(
        name=name
    )

    await state.set_state(
        AddProductFSM.description
    )

    await message.answer(
        "📝 Введите <b>описание товара</b>:",
        parse_mode="HTML"
    )


@router.message(AddProductFSM.description)
async def process_description(
    message: Message,
    state: FSMContext
):
    description = message.text.strip()

    if not description:
        await message.answer(
            "❌ Описание товара не может быть пустым."
        )
        return

    await state.update_data(
        description=description
    )

    await state.set_state(
        AddProductFSM.price
    )

    await message.answer(
        "💰 Введите <b>цену товара</b> (числом):",
        parse_mode="HTML"
    )


@router.message(AddProductFSM.price)
async def process_price(
    message: Message,
    state: FSMContext
):
    try:
        price_val = Decimal(
            message.text.replace(",", ".")
        )

        if price_val <= 0:
            raise ValueError

    except (ValueError, InvalidOperation):
        await message.answer(
            "❌ Ошибка! Введите корректное "
            "положительное число для цены."
        )
        return

    await state.update_data(
        price=price_val
    )

    await state.set_state(
        AddProductFSM.stock
    )

    await message.answer(
        "🔢 Введите <b>количество товара "
        "на складе</b> (шт):",
        parse_mode="HTML"
    )


@router.message(AddProductFSM.stock)
async def process_stock(
    message: Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer(
            "❌ Ошибка! Количество должно быть "
            "целым числом."
        )
        return

    stock = int(message.text)

    if stock < 0:
        await message.answer(
            "❌ Количество не может быть отрицательным."
        )
        return

    await state.update_data(
        stock=stock
    )

    await state.set_state(
        AddProductFSM.category
    )

    await message.answer(
        "🏷 Введите <b>категорию товара</b> "
        "(например: <i>Обувь</i>, <i>Одежда</i>):",
        parse_mode="HTML"
    )


@router.message(AddProductFSM.category)
async def process_category(
    message: Message,
    state: FSMContext
):
    category = message.text.strip()

    if not category:
        await message.answer(
            "❌ Категория не может быть пустой."
        )
        return

    await state.update_data(
        category=category
    )

    await state.set_state(
        AddProductFSM.photo
    )

    await message.answer(
        "📸 Отправьте <b>изображение товара</b> "
        "(как фото):",
        parse_mode="HTML"
    )


@router.message(AddProductFSM.photo, F.photo)
async def process_photo(
    message: Message,
    state: FSMContext
):
    photo_id = message.photo[-1].file_id

    data = await state.get_data()

    conn = await get_connection()

    try:
        await conn.execute(
            """
            INSERT INTO products
            (name, description, price, stock, category, image_id)
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

    formatted_price = (
        f"{data['price']:,.0f}"
        .replace(",", " ")
    )

    await message.answer_photo(
        photo=photo_id,
        caption=(
            "✅ <b>Товар успешно добавлен "
            "в базу!</b>\n\n"
            f"📌 <b>Название:</b> {data['name']}\n"
            f"📝 <b>Описание:</b> "
            f"{data['description']}\n"
            f"💰 <b>Цена:</b> "
            f"{formatted_price} ₽\n"
            f"🔢 <b>На складе:</b> "
            f"{data['stock']} шт.\n"
            f"🏷 <b>Категория:</b> "
            f"{data['category']}"
        ),
        parse_mode="HTML"
    )
    
@router.message(AddProductFSM.photo)
async def process_invalid_photo(message: Message):
    await message.answer(
        "❌ Нужно отправить именно фотографию.\n"
        "Попробуйте ещё раз."
    )