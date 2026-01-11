"""Тесты для Pydantic схем."""

import pytest
from pydantic import ValidationError

from src.app.objects.schema import ObjectCreate, ObjectRead, ObjectUpdate
from src.app.users.schema import UserCreate, UserRead, UserUpdate


class TestUserSchemas:
    """Тесты для схем пользователя."""

    def test_user_create_valid(self, user_data: dict):
        """Тест создания валидной схемы UserCreate."""
        user = UserCreate(**user_data)
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.full_name == user_data["full_name"]
        assert user.telegram_id == user_data["telegram_id"]

    def test_user_create_missing_field(self, user_data: dict):
        """Тест создания UserCreate без обязательного поля."""
        del user_data["first_name"]
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "first_name" in str(exc_info.value)

    def test_user_update_valid(self, user_data: dict):
        """Тест создания валидной схемы UserUpdate."""
        user = UserUpdate(**user_data)
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]

    def test_user_read_valid(self, user_data: dict):
        """Тест создания валидной схемы UserRead."""
        user_data_with_id = {"id": 1, **user_data}
        user = UserRead(**user_data_with_id)
        assert user.id == 1
        assert user.first_name == user_data["first_name"]

    def test_user_read_missing_id(self, user_data: dict):
        """Тест создания UserRead без id."""
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**user_data)
        assert "id" in str(exc_info.value)

    def test_user_create_type_coercion_raises(self):
        """Тест строгой валидации типов в UserCreate (int не конвертируется в str)."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                first_name="Test",
                last_name="User",
                full_name="Test User",
                telegram_id=12345,  # int вместо str - вызывает ошибку
            )
        assert "telegram_id" in str(exc_info.value)


class TestObjectSchemas:
    """Тесты для схем объекта."""

    def test_object_create_valid(self, object_data: dict):
        """Тест создания валидной схемы ObjectCreate."""
        obj = ObjectCreate(**object_data)
        assert obj.name == object_data["name"]
        assert obj.point == object_data["point"]
        assert obj.user_id == object_data["user_id"]

    def test_object_create_missing_field(self, object_data: dict):
        """Тест создания ObjectCreate без обязательного поля."""
        del object_data["name"]
        with pytest.raises(ValidationError) as exc_info:
            ObjectCreate(**object_data)
        assert "name" in str(exc_info.value)

    def test_object_update_valid(self):
        """Тест создания валидной схемы ObjectUpdate."""
        obj = ObjectUpdate(name="Физика", point=90)
        assert obj.name == "Физика"
        assert obj.point == 90

    def test_object_read_valid(self, object_data: dict):
        """Тест создания валидной схемы ObjectRead."""
        object_data_with_id = {"id": 1, **object_data}
        obj = ObjectRead(**object_data_with_id)
        assert obj.id == 1
        assert obj.name == object_data["name"]
        assert obj.point == object_data["point"]

    def test_object_create_invalid_point_type(self, object_data: dict):
        """Тест создания ObjectCreate с невалидным типом point."""
        object_data["point"] = "not_a_number"
        with pytest.raises(ValidationError) as exc_info:
            ObjectCreate(**object_data)
        assert "point" in str(exc_info.value)

    def test_object_create_negative_point(self, object_data: dict):
        """Тест создания ObjectCreate с отрицательным баллом (допустимо по схеме)."""
        object_data["point"] = -10
        obj = ObjectCreate(**object_data)
        assert obj.point == -10

    def test_object_create_high_point(self, object_data: dict):
        """Тест создания ObjectCreate с высоким баллом (допустимо по схеме)."""
        object_data["point"] = 150
        obj = ObjectCreate(**object_data)
        assert obj.point == 150
