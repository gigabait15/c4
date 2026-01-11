"""Тесты для API клиента бота."""

import pytest
from aioresponses import aioresponses

from bot.api_client import APIClient


class TestAPIClient:
    """Тесты для APIClient."""

    @pytest.fixture
    def api_client(self) -> APIClient:
        """Создать экземпляр API клиента."""
        return APIClient(base_url="http://test-api")

    @pytest.mark.asyncio
    async def test_get_user_success(self, api_client: APIClient):
        """Тест успешного получения пользователя."""
        user_data = {
            "id": 1,
            "first_name": "Иван",
            "last_name": "Иванов",
            "full_name": "Иван Иванов",
            "telegram_id": "123456789",
        }

        with aioresponses() as m:
            m.get("http://test-api/users/1", payload=user_data)

            result = await api_client.get_user(1)

            assert result == user_data

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, api_client: APIClient):
        """Тест получения несуществующего пользователя."""
        with aioresponses() as m:
            m.get("http://test-api/users/999", status=404)

            result = await api_client.get_user(999)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_success(self, api_client: APIClient):
        """Тест успешного получения пользователя по telegram_id."""
        user_data = {
            "id": 1,
            "first_name": "Иван",
            "last_name": "Иванов",
            "full_name": "Иван Иванов",
            "telegram_id": "123456789",
        }

        with aioresponses() as m:
            m.get("http://test-api/users/telegram/123456789", payload=user_data)

            result = await api_client.get_user_by_telegram_id("123456789")

            assert result == user_data

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_not_found(self, api_client: APIClient):
        """Тест получения пользователя по несуществующему telegram_id."""
        with aioresponses() as m:
            m.get("http://test-api/users/telegram/nonexistent", status=404)

            result = await api_client.get_user_by_telegram_id("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(self, api_client: APIClient):
        """Тест успешного создания пользователя."""
        expected_response = {
            "id": 1,
            "first_name": "Иван",
            "last_name": "Иванов",
            "full_name": "Иван Иванов",
            "telegram_id": "123456789",
        }

        with aioresponses() as m:
            m.post("http://test-api/users/", payload=expected_response)

            result = await api_client.create_user(
                first_name="Иван",
                last_name="Иванов",
                full_name="Иван Иванов",
                telegram_id="123456789",
            )

            assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_user_error(self, api_client: APIClient):
        """Тест ошибки при создании пользователя."""
        with aioresponses() as m:
            m.post("http://test-api/users/", status=500, body="Internal Server Error")

            with pytest.raises(Exception) as exc_info:
                await api_client.create_user(
                    first_name="Иван",
                    last_name="Иванов",
                    full_name="Иван Иванов",
                    telegram_id="123456789",
                )

            assert "API Error 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_objects_by_user_id_success(self, api_client: APIClient):
        """Тест успешного получения объектов пользователя."""
        objects_data = [
            {"id": 1, "name": "Математика", "point": 85, "user_id": 1},
            {"id": 2, "name": "Русский язык", "point": 92, "user_id": 1},
        ]

        with aioresponses() as m:
            m.get("http://test-api/objects/1", payload=objects_data)

            result = await api_client.get_objects_by_user_id(1)

            assert result == objects_data

    @pytest.mark.asyncio
    async def test_get_objects_by_user_id_empty(self, api_client: APIClient):
        """Тест получения пустого списка объектов."""
        with aioresponses() as m:
            m.get("http://test-api/objects/1", payload=[])

            result = await api_client.get_objects_by_user_id(1)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_objects_by_user_id_not_found(self, api_client: APIClient):
        """Тест получения объектов для несуществующего пользователя."""
        with aioresponses() as m:
            m.get("http://test-api/objects/999", status=404)

            result = await api_client.get_objects_by_user_id(999)

            assert result == []

    @pytest.mark.asyncio
    async def test_create_object_success(self, api_client: APIClient):
        """Тест успешного создания объекта."""
        expected_response = {
            "id": 1,
            "name": "Математика",
            "point": 85,
            "user_id": 1,
        }

        with aioresponses() as m:
            m.post("http://test-api/objects/", payload=expected_response)

            result = await api_client.create_object(
                name="Математика",
                point=85,
                user_id=1,
            )

            assert result == expected_response

    @pytest.mark.asyncio
    async def test_create_object_duplicate_error(self, api_client: APIClient):
        """Тест ошибки при создании дублирующего объекта."""
        with aioresponses() as m:
            m.post(
                "http://test-api/objects/",
                status=400,
                body='{"detail": "Object already exists"}',
            )

            with pytest.raises(Exception) as exc_info:
                await api_client.create_object(
                    name="Математика",
                    point=85,
                    user_id=1,
                )

            assert "API Error 400" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_request_with_params(self, api_client: APIClient):
        """Тест запроса с параметрами."""
        user_data = {"id": 1, "first_name": "Test"}

        with aioresponses() as m:
            m.get(
                "http://test-api/users/1?key=value",
                payload=user_data,
            )

            result = await api_client._request(
                "GET", "/users/1", params={"key": "value"}
            )

            assert result == user_data

