from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

SUBJECTS = [
    "Математика",
    "Русский язык",
    "Физика",
    "Химия",
    "Биология",
    "История",
    "Обществознание",
    "Информатика",
    "Литература",
    "Английский язык",
]


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📚 Выбрать предмет"),
                KeyboardButton(text="📊 Мои баллы"),
            ],
        ],
        resize_keyboard=True,
    )


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для незарегистрированных."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Зарегистрироваться")],
        ],
        resize_keyboard=True,
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def get_subjects_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора предмета."""
    buttons = []
    for i in range(0, len(SUBJECTS), 2):
        row = [KeyboardButton(text=SUBJECTS[i])]
        if i + 1 < len(SUBJECTS):
            row.append(KeyboardButton(text=SUBJECTS[i + 1]))
        buttons.append(row)
    buttons.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardRemove:
    """Убрать клавиатуру."""
    return ReplyKeyboardRemove()
