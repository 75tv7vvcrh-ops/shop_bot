from aiogram.dispatcher.middlewares.base import BaseMiddleware
from config import ADMIN_ID
from services.database import is_user_banned

class BanMiddleware(BaseMiddleware):
    """Проверяет входящие события: если пользователь в бане — отклоняет запрос."""
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        
        # Администратора банить нельзя
        if user_id != ADMIN_ID and await is_user_banned(user_id):
            if hasattr(event, "answer"):
                await event.answer("🚫 Вы заблокированы и не можете использовать бота.")
            return

        return await handler(event, data)

class RoleMiddleware(BaseMiddleware):
    """Прокидывает роль пользователя ('admin' или 'user') в хэндлеры."""
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        data["role"] = "admin" if user_id == ADMIN_ID else "user"
        return await handler(event, data)