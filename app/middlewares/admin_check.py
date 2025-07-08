from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.db.database import Database


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, db: Database) -> bool:
        user = await db.get_user(message.from_user.id)
        return bool(user and user.get("is_admin"))
