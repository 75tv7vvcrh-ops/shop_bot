from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

# Глобальный словарь для хранения забаненных пользователей: {user_id: reason}
banned_users: Dict[int, str] = {}


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id and user_id in banned_users:
            reason = banned_users[user_id]
            if isinstance(event, Message):
                await event.answer(f"⛔ **Вы заблокированы!**\nПричина: {reason}", parse_mode="Markdown")
            elif isinstance(event, CallbackQuery):
                await event.answer(f"⛔ Вы заблокированы. Причина: {reason}", show_alert=True)
            return  # Прерываем обработку события

        return await handler(event, data)