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

        result = await self.db.execute("SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,))
        user = await result.fetchone()

        data["is_registered"] = bool(user)

        return await handler(event, data)
