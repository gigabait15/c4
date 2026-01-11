from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_db
from src.app.objects.crud import ObjectCRUD
from src.app.objects.model import Object
from src.app.objects.schema import ObjectCreate


class ObjectService:
    def __init__(self, db: AsyncSession, object_crud: ObjectCRUD):
        self.object_crud = object_crud
        self.db = db

    async def create_new_object(
        self, user_id: int, object_in: ObjectCreate
    ) -> Object | None:
        obj = await self.object_crud.get_object_by_user_id_and_object_name(
            self.db, user_id, object_in.name
        )
        if obj is None:
            return await self.object_crud.create(self.db, obj_in=object_in)
        else:
            return None


async def object_service(db: AsyncSession = Depends(get_db)) -> ObjectService:
    return ObjectService(db=db, object_crud=ObjectCRUD(Object))
