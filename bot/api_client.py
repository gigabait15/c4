from typing import Any

import aiohttp

from core.base.config import settings


class APIClient:
    """HTTP клиент для взаимодействия с API."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.API_BASE_URL

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Выполнить HTTP запрос."""
        url = f"{self.base_url}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params,
            ) as response:
                if response.status == 404:
                    return None
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API Error {response.status}: {error}")
                return await response.json()

    # ================== Users ==================

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        """Получить пользователя по ID."""
        return await self._request("GET", f"/users/{user_id}")

    async def get_user_by_telegram_id(self, telegram_id: str) -> dict[str, Any] | None:
        """Получить пользователя по telegram_id."""
        return await self._request("GET", f"/users/telegram/{telegram_id}")

    async def create_user(
        self,
        first_name: str,
        last_name: str,
        full_name: str,
        telegram_id: str,
    ) -> dict[str, Any]:
        """Создать пользователя."""
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "telegram_id": telegram_id,
        }
        result = await self._request("POST", "/users/", data=data)
        return result or {}

    # ================== Objects (Scores) ==================

    async def get_objects_by_user_id(self, user_id: int) -> list[dict[str, Any]]:
        """Получить все объекты пользователя."""
        result = await self._request("GET", f"/objects/{user_id}")
        return result if isinstance(result, list) else []

    async def create_object(
        self,
        name: str,
        point: int,
        user_id: int,
    ) -> dict[str, Any]:
        """Создать объект (балл)."""
        data = {
            "name": name,
            "point": point,
            "user_id": user_id,
        }
        result = await self._request("POST", "/objects/", data=data)
        return result or {}


# Глобальный экземпляр клиента
api_client = APIClient()
