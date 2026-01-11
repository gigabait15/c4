import logging
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("crud")


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @staticmethod
    def _to_dict(obj: ModelType) -> dict[str, Any]:
        """Конвертировать объект модели в словарь."""
        return {
            column.name: getattr(obj, column.name) for column in obj.__table__.columns
        }

    async def get_by_id(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Получить объект по ID."""
        logger.debug("Получение %s по id=%s", self.model.__name__, id)
        result = await db.get(self.model, id)
        if result is None:
            logger.warning("%s с id=%s не найден", self.model.__name__, id)
            return None
        return result

    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Получить список объектов с пагинацией."""
        logger.debug(
            "Получение списка %s (skip=%d, limit=%d)", self.model.__name__, skip, limit
        )
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        logger.debug("Получено %d записей %s", len(items), self.model.__name__)
        return items

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Создать новый объект."""
        logger.info("Создание %s: %s", self.model.__name__, obj_in)
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(
            "Создан %s с id=%s", self.model.__name__, getattr(db_obj, "id", "?")
        )
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        id: Any,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType | None:
        """Обновить объект по ID."""
        logger.info("Обновление %s с id=%s", self.model.__name__, id)
        db_obj = await self.get_by_id(db, id)
        if db_obj is None:
            logger.warning(
                "Не удалось обновить: %s с id=%s не найден", self.model.__name__, id
            )
            return None

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        logger.debug("Обновляемые поля: %s", list(update_data.keys()))
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        logger.info("Обновлён %s с id=%s", self.model.__name__, id)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        """Удалить объект по ID."""
        logger.info("Удаление %s с id=%s", self.model.__name__, id)
        db_obj = await self.get_by_id(db, id)
        if db_obj is None:
            logger.warning(
                "Не удалось удалить: %s с id=%s не найден", self.model.__name__, id
            )
            return None

        await db.delete(db_obj)
        await db.commit()
        logger.info("Удалён %s с id=%s", self.model.__name__, id)
        return db_obj
