"""Тесты для CRUD операций."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.objects.crud import ObjectCRUD, object_crud
from src.app.objects.model import Object
from src.app.objects.schema import ObjectCreate
from src.app.users.crud import UserCRUD, user_crud
from src.app.users.model import User
from src.app.users.schema import UserCreate, UserUpdate


class TestUserCRUD:
    """Тесты для CRUD операций пользователя."""

    @pytest_asyncio.fixture
    async def created_user(
        self, async_db_session: AsyncSession, user_data: dict
    ) -> User:
        """Создать тестового пользователя."""
        user_in = UserCreate(**user_data)
        user = await user_crud.create(async_db_session, obj_in=user_in)
        return user

    @pytest.mark.asyncio
    async def test_create_user(self, async_db_session: AsyncSession, user_data: dict):
        """Тест создания пользователя."""
        user_in = UserCreate(**user_data)
        user = await user_crud.create(async_db_session, obj_in=user_in)

        assert user.id is not None
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.full_name == user_data["full_name"]
        assert user.telegram_id == user_data["telegram_id"]

    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self, async_db_session: AsyncSession, created_user: User
    ):
        """Тест получения пользователя по ID."""
        user = await user_crud.get_by_id(async_db_session, created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.telegram_id == created_user.telegram_id

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, async_db_session: AsyncSession):
        """Тест получения несуществующего пользователя."""
        user = await user_crud.get_by_id(async_db_session, 99999)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id(
        self, async_db_session: AsyncSession, created_user: User
    ):
        """Тест получения пользователя по telegram_id."""
        user = await user_crud.get_user_by_telegram_id(
            async_db_session, created_user.telegram_id
        )

        assert user is not None
        assert user.id == created_user.id
        assert user.telegram_id == created_user.telegram_id

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_not_found(
        self, async_db_session: AsyncSession
    ):
        """Тест получения пользователя по несуществующему telegram_id."""
        user = await user_crud.get_user_by_telegram_id(
            async_db_session, "nonexistent_telegram_id"
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_get_all_users(
        self, async_db_session: AsyncSession, user_data: dict, user_data_2: dict
    ):
        """Тест получения списка пользователей."""
        # Создаём двух пользователей
        await user_crud.create(async_db_session, obj_in=UserCreate(**user_data))
        await user_crud.create(async_db_session, obj_in=UserCreate(**user_data_2))

        users = await user_crud.get_all(async_db_session)

        assert len(users) >= 2

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(
        self, async_db_session: AsyncSession, user_data: dict, user_data_2: dict
    ):
        """Тест пагинации при получении списка пользователей."""
        await user_crud.create(async_db_session, obj_in=UserCreate(**user_data))
        await user_crud.create(async_db_session, obj_in=UserCreate(**user_data_2))

        users = await user_crud.get_all(async_db_session, skip=0, limit=1)

        assert len(users) == 1

    @pytest.mark.asyncio
    async def test_update_user(
        self, async_db_session: AsyncSession, created_user: User
    ):
        """Тест обновления пользователя."""
        update_data = UserUpdate(
            first_name="Новое Имя",
            last_name="Новая Фамилия",
            full_name="Новое Имя Новая Фамилия",
            telegram_id=created_user.telegram_id,
        )

        updated_user = await user_crud.update(
            async_db_session, id=created_user.id, obj_in=update_data
        )

        assert updated_user is not None
        assert updated_user.first_name == "Новое Имя"
        assert updated_user.last_name == "Новая Фамилия"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, async_db_session: AsyncSession):
        """Тест обновления несуществующего пользователя."""
        update_data = UserUpdate(
            first_name="Test",
            last_name="Test",
            full_name="Test Test",
            telegram_id="123",
        )

        updated_user = await user_crud.update(
            async_db_session, id=99999, obj_in=update_data
        )

        assert updated_user is None

    @pytest.mark.asyncio
    async def test_delete_user(
        self, async_db_session: AsyncSession, created_user: User
    ):
        """Тест удаления пользователя."""
        deleted_user = await user_crud.delete(async_db_session, id=created_user.id)

        assert deleted_user is not None
        assert deleted_user.id == created_user.id

        # Проверяем, что пользователь удалён
        user = await user_crud.get_by_id(async_db_session, created_user.id)
        assert user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, async_db_session: AsyncSession):
        """Тест удаления несуществующего пользователя."""
        deleted_user = await user_crud.delete(async_db_session, id=99999)
        assert deleted_user is None


class TestObjectCRUD:
    """Тесты для CRUD операций объекта."""

    @pytest_asyncio.fixture
    async def created_user(
        self, async_db_session: AsyncSession, user_data: dict
    ) -> User:
        """Создать тестового пользователя для объектов."""
        user_in = UserCreate(**user_data)
        user = await user_crud.create(async_db_session, obj_in=user_in)
        return user

    @pytest_asyncio.fixture
    async def created_object(
        self, async_db_session: AsyncSession, created_user: User, object_data: dict
    ) -> Object:
        """Создать тестовый объект."""
        object_data["user_id"] = created_user.id
        obj_in = ObjectCreate(**object_data)
        obj = await object_crud.create(async_db_session, obj_in=obj_in)
        return obj

    @pytest.mark.asyncio
    async def test_create_object(
        self, async_db_session: AsyncSession, created_user: User, object_data: dict
    ):
        """Тест создания объекта."""
        object_data["user_id"] = created_user.id
        obj_in = ObjectCreate(**object_data)
        obj = await object_crud.create(async_db_session, obj_in=obj_in)

        assert obj.id is not None
        assert obj.name == object_data["name"]
        assert obj.point == object_data["point"]
        assert obj.user_id == created_user.id

    @pytest.mark.asyncio
    async def test_get_object_by_id(
        self, async_db_session: AsyncSession, created_object: Object
    ):
        """Тест получения объекта по ID."""
        obj = await object_crud.get_by_id(async_db_session, created_object.id)

        assert obj is not None
        assert obj.id == created_object.id
        assert obj.name == created_object.name

    @pytest.mark.asyncio
    async def test_get_all_objects_by_user_id(
        self,
        async_db_session: AsyncSession,
        created_user: User,
        object_data: dict,
        object_data_2: dict,
    ):
        """Тест получения всех объектов пользователя."""
        object_data["user_id"] = created_user.id
        object_data_2["user_id"] = created_user.id

        await object_crud.create(async_db_session, obj_in=ObjectCreate(**object_data))
        await object_crud.create(async_db_session, obj_in=ObjectCreate(**object_data_2))

        objects = await object_crud.get_all_objects_by_user_id(
            async_db_session, created_user.id
        )

        assert len(objects) == 2
        assert all(obj.user_id == created_user.id for obj in objects)

    @pytest.mark.asyncio
    async def test_get_all_objects_by_user_id_empty(
        self, async_db_session: AsyncSession, created_user: User
    ):
        """Тест получения объектов для пользователя без объектов."""
        objects = await object_crud.get_all_objects_by_user_id(
            async_db_session, created_user.id
        )

        assert objects == []

    @pytest.mark.asyncio
    async def test_get_object_by_user_id_and_name(
        self, async_db_session: AsyncSession, created_object: Object
    ):
        """Тест получения объекта по user_id и имени."""
        obj = await object_crud.get_object_by_user_id_and_object_name(
            async_db_session, created_object.user_id, created_object.name
        )

        assert obj is not None
        assert obj.id == created_object.id
        assert obj.name == created_object.name

    @pytest.mark.asyncio
    async def test_get_object_by_user_id_and_name_not_found(
        self, async_db_session: AsyncSession, created_user: User
    ):
        """Тест получения несуществующего объекта."""
        obj = await object_crud.get_object_by_user_id_and_object_name(
            async_db_session, created_user.id, "Несуществующий предмет"
        )

        assert obj is None

    @pytest.mark.asyncio
    async def test_delete_object(
        self, async_db_session: AsyncSession, created_object: Object
    ):
        """Тест удаления объекта."""
        deleted_obj = await object_crud.delete(async_db_session, id=created_object.id)

        assert deleted_obj is not None
        assert deleted_obj.id == created_object.id

        # Проверяем, что объект удалён
        obj = await object_crud.get_by_id(async_db_session, created_object.id)
        assert obj is None

