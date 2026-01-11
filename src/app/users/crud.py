from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.crud import CRUDBase
from src.app.users.model import User
from src.app.users.schema import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_user_by_telegram_id(
        self, db: AsyncSession, telegram_id: str
    ) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


user_crud = UserCRUD(User)
