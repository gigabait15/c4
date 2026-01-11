"""Тесты для сервисов."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.objects.crud import ObjectCRUD, object_crud
from src.app.objects.model import Object
from src.app.objects.schema import ObjectCreate
from src.app.objects.service import ObjectService
from src.app.users.crud import user_crud
from src.app.users.model import User
from src.app.users.schema import UserCreate


class TestObjectService:
    """Тесты для ObjectService."""

    @pytest_asyncio.fixture
    async def created_user(
        self, async_db_session: AsyncSession, user_data: dict
    ) -> User:
        """Создать тестового пользователя."""
        user_in = UserCreate(**user_data)
        user = await user_crud.create(async_db_session, obj_in=user_in)
        return user

    @pytest.fixture
    def object_service(self, async_db_session: AsyncSession) -> ObjectService:
        """Создать экземпляр ObjectService."""
        return ObjectService(db=async_db_session, object_crud=ObjectCRUD(Object))

    @pytest.mark.asyncio
    async def test_create_new_object_success(
        self,
        async_db_session: AsyncSession,
        object_service: ObjectService,
        created_user: User,
        object_data: dict,
    ):
        """Тест успешного создания нового объекта."""
        object_data["user_id"] = created_user.id
        obj_in = ObjectCreate(**object_data)

        obj = await object_service.create_new_object(
            user_id=created_user.id, object_in=obj_in
        )

        assert obj is not None
        assert obj.name == object_data["name"]
        assert obj.point == object_data["point"]
        assert obj.user_id == created_user.id

    @pytest.mark.asyncio
    async def test_create_new_object_duplicate(
        self,
        async_db_session: AsyncSession,
        object_service: ObjectService,
        created_user: User,
        object_data: dict,
    ):
        """Тест создания дубликата объекта (должен вернуть None)."""
        object_data["user_id"] = created_user.id
        obj_in = ObjectCreate(**object_data)

        # Создаём первый объект
        obj1 = await object_service.create_new_object(
            user_id=created_user.id, object_in=obj_in
        )
        assert obj1 is not None

        # Пытаемся создать дубликат
        obj2 = await object_service.create_new_object(
            user_id=created_user.id, object_in=obj_in
        )
        assert obj2 is None

    @pytest.mark.asyncio
    async def test_create_new_object_same_name_different_user(
        self,
        async_db_session: AsyncSession,
        created_user: User,
        user_data_2: dict,
        object_data: dict,
    ):
        """Тест создания объекта с одинаковым именем для разных пользователей."""
        # Создаём второго пользователя
        user2 = await user_crud.create(
            async_db_session, obj_in=UserCreate(**user_data_2)
        )

        # Создаём сервисы для каждого пользователя
        service = ObjectService(db=async_db_session, object_crud=ObjectCRUD(Object))

        # Создаём объект для первого пользователя
        object_data["user_id"] = created_user.id
        obj_in_1 = ObjectCreate(**object_data)
        obj1 = await service.create_new_object(
            user_id=created_user.id, object_in=obj_in_1
        )

        # Создаём объект с таким же именем для второго пользователя
        object_data["user_id"] = user2.id
        obj_in_2 = ObjectCreate(**object_data)
        obj2 = await service.create_new_object(user_id=user2.id, object_in=obj_in_2)

        # Оба объекта должны быть созданы
        assert obj1 is not None
        assert obj2 is not None
        assert obj1.name == obj2.name
        assert obj1.user_id != obj2.user_id

    @pytest.mark.asyncio
    async def test_create_new_object_different_names_same_user(
        self,
        async_db_session: AsyncSession,
        object_service: ObjectService,
        created_user: User,
        object_data: dict,
        object_data_2: dict,
    ):
        """Тест создания объектов с разными именами для одного пользователя."""
        object_data["user_id"] = created_user.id
        object_data_2["user_id"] = created_user.id

        obj_in_1 = ObjectCreate(**object_data)
        obj_in_2 = ObjectCreate(**object_data_2)

        obj1 = await object_service.create_new_object(
            user_id=created_user.id, object_in=obj_in_1
        )
        obj2 = await object_service.create_new_object(
            user_id=created_user.id, object_in=obj_in_2
        )

        # Оба объекта должны быть созданы
        assert obj1 is not None
        assert obj2 is not None
        assert obj1.name != obj2.name
        assert obj1.user_id == obj2.user_id

