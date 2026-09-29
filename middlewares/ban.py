from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import ADMIN_ID
from services.database import is_user_banned


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        user_id = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id

        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        # Администратор не блокируется
        if user_id == ADMIN_ID:
            return await handler(event, data)

        if user_id:
            banned_user = await is_user_banned(user_id)

            if banned_user:
                reason = banned_user["reason"]

                if isinstance(event, Message):
                    await event.answer(
                        f"⛔ <b>Вы заблокированы.</b>\n\n"
                        f"Причина: {reason}",
                        parse_mode="HTML"
                    )

                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"⛔ Вы заблокированы.\nПричина: {reason}",
                        show_alert=True
                    )

                return

        return await handler(event, data)