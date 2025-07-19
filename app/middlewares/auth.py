from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any

class AuthMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        telegram_id = event.from_user.id

        user = await self.db.fetchone("SELECT is_admin FROM users WHERE telegram_id = $1", (telegram_id,))

        data["is_registered"] = bool(user)
        data["is_admin"] = bool(user and user[0]) if user else False

        return await handler(event, data)
