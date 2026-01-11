from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.crud import CRUDBase
from src.app.objects.model import Object
from src.app.objects.schema import ObjectCreate, ObjectUpdate


class ObjectCRUD(CRUDBase[Object, ObjectCreate, ObjectUpdate]):

    async def get_all_objects_by_user_id(
        self, db: AsyncSession, user_id: int
    ) -> list[Object]:
        stmt = select(Object).where(Object.user_id == user_id)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        return items

    async def get_object_by_user_id_and_object_name(
        self, db: AsyncSession, user_id: int, object_name: str
    ) -> Object | None:
        stmt = select(Object).where(
            Object.user_id == user_id, Object.name == object_name
        )
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()
        return item


object_crud = ObjectCRUD(Object)
