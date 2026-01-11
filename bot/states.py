from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """Состояния пользователя."""

    user_id: int | None = None  # ID пользователя в БД


class RegistrationState(StatesGroup):
    """Состояния регистрации."""

    waiting_first_name = State()
    waiting_last_name = State()


class ScoreState(StatesGroup):
    """Состояния ввода баллов."""

    waiting_subject = State()
    waiting_score = State()
