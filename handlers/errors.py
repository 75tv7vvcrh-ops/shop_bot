import logging

from aiogram import Router
from aiogram.types import ErrorEvent


router = Router()


@router.error()
async def global_error_handler(event: ErrorEvent):
    logging.error(
        "Ошибка при обработке update: %s",
        event.exception,
        exc_info=True
    )

    if event.update.message:
        try:
            await event.update.message.answer(
                "❌ Что-то пошло не так. Попробуй ещё раз."
            )
        except Exception:
            pass

    elif event.update.callback_query:
        try:
            await event.update.callback_query.answer(
                "❌ Произошла ошибка. Попробуй ещё раз.",
                show_alert=True
            )
        except Exception:
            pass