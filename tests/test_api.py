"""Интеграционные тесты для API endpoints."""

import pytest
from httpx import AsyncClient


class TestUsersAPI:
    """Тесты для API пользователей."""

    @pytest.mark.asyncio
    async def test_create_user(self, async_client: AsyncClient, user_data: dict):
        """Тест создания пользователя через API."""
        response = await async_client.post("/users/", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert data["full_name"] == user_data["full_name"]
        assert data["telegram_id"] == user_data["telegram_id"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_client: AsyncClient, user_data: dict):
        """Тест получения пользователя по ID через API."""
        # Создаём пользователя
        create_response = await async_client.post("/users/", json=user_data)
        created_user = create_response.json()

        # Получаем пользователя
        response = await async_client.get(f"/users/{created_user['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["telegram_id"] == user_data["telegram_id"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, async_client: AsyncClient):
        """Тест получения несуществующего пользователя."""
        response = await async_client.get("/users/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id(
        self, async_client: AsyncClient, user_data: dict
    ):
        """Тест получения пользователя по telegram_id."""
        # Создаём пользователя
        await async_client.post("/users/", json=user_data)

        # Получаем по telegram_id
        response = await async_client.get(f"/users/telegram/{user_data['telegram_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == user_data["telegram_id"]
        assert data["first_name"] == user_data["first_name"]

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_not_found(self, async_client: AsyncClient):
        """Тест получения пользователя по несуществующему telegram_id."""
        response = await async_client.get("/users/telegram/nonexistent_id")

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_create_user_missing_field(self, async_client: AsyncClient):
        """Тест создания пользователя с отсутствующим полем."""
        incomplete_data = {
            "first_name": "Test",
            "last_name": "User",
            # missing full_name and telegram_id
        }
        response = await async_client.post("/users/", json=incomplete_data)

        assert response.status_code == 422  # Validation error


class TestObjectsAPI:
    """Тесты для API объектов."""

    @pytest.fixture
    async def created_user(self, async_client: AsyncClient, user_data: dict) -> dict:
        """Создать пользователя для тестов объектов."""
        response = await async_client.post("/users/", json=user_data)
        return response.json()

    @pytest.mark.asyncio
    async def test_create_object(
        self, async_client: AsyncClient, created_user: dict, object_data: dict
    ):
        """Тест создания объекта через API."""
        object_data["user_id"] = created_user["id"]

        response = await async_client.post("/objects/", json=object_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == object_data["name"]
        assert data["point"] == object_data["point"]
        assert data["user_id"] == created_user["id"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_object_duplicate(
        self, async_client: AsyncClient, created_user: dict, object_data: dict
    ):
        """Тест создания дублирующего объекта (должен вернуть ошибку)."""
        object_data["user_id"] = created_user["id"]

        # Создаём первый объект
        response1 = await async_client.post("/objects/", json=object_data)
        assert response1.status_code == 200

        # Пытаемся создать дубликат
        response2 = await async_client.post("/objects/", json=object_data)
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Object already exists"

    @pytest.mark.asyncio
    async def test_get_objects_by_user_id(
        self,
        async_client: AsyncClient,
        created_user: dict,
        object_data: dict,
        object_data_2: dict,
    ):
        """Тест получения всех объектов пользователя."""
        object_data["user_id"] = created_user["id"]
        object_data_2["user_id"] = created_user["id"]

        # Создаём два объекта
        await async_client.post("/objects/", json=object_data)
        await async_client.post("/objects/", json=object_data_2)

        # Получаем все объекты
        response = await async_client.get(f"/objects/{created_user['id']}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [obj["name"] for obj in data]
        assert object_data["name"] in names
        assert object_data_2["name"] in names

    @pytest.mark.asyncio
    async def test_get_objects_by_user_id_empty(
        self, async_client: AsyncClient, created_user: dict
    ):
        """Тест получения объектов для пользователя без объектов."""
        response = await async_client.get(f"/objects/{created_user['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_create_object_missing_field(
        self, async_client: AsyncClient, created_user: dict
    ):
        """Тест создания объекта с отсутствующим полем."""
        incomplete_data = {
            "name": "Математика",
            # missing point and user_id
        }
        response = await async_client.post("/objects/", json=incomplete_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_object_invalid_point(
        self, async_client: AsyncClient, created_user: dict
    ):
        """Тест создания объекта с невалидным баллом."""
        invalid_data = {
            "name": "Математика",
            "point": "not_a_number",
            "user_id": created_user["id"],
        }
        response = await async_client.post("/objects/", json=invalid_data)

        assert response.status_code == 422  # Validation error
