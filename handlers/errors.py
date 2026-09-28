import logging
from aiogram.types import ErrorEvent

from bot import router


@router.error()
async def global_error_handler(event: ErrorEvent):
    logging.error(f"Ошибка в боте: {event.exception}")
    if event.update.message:
        await event.update.message.answer("❌ Что-то пошло не так. Попробуй ещё раз.")