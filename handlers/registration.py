from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.registration import Registration
from services.database import save_user_profile

router = Router()

@router.message(F.text == "📝 Регистрация")
async def register_command(message: Message, state: FSMContext):
    await message.answer("Как тебя зовут?")
    await state.set_state(Registration.name)

@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("Пожалуйста, введи имя.")
        return
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Registration.age)

@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 14 or age > 100:
            await message.answer("Пожалуйста, укажи реальный возраст (14-100).")
            return
        await state.update_data(age=age)
        await message.answer("В каком городе ты живёшь?")
        await state.set_state(Registration.city)
    except ValueError:
        await message.answer("Пожалуйста, введи число.")

@router.message(Registration.city)
async def process_city(message: Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("Пожалуйста, введи название города.")
        return
    
    await state.update_data(city=message.text)
    data = await state.get_data()

    await save_user_profile(
        user_id=message.from_user.id,
        name=data['name'],
        age=data['age'],
        city=data['city']
    )

    await message.answer(
        f"✅ Регистрация завершена и сохранена в профиль!\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Город: {data['city']}"
    )
    await state.clear()