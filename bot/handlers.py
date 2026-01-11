from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.api_client import api_client
from bot.keyboards import (
    SUBJECTS,
    get_cancel_keyboard,
    get_main_keyboard,
    get_start_keyboard,
    get_subjects_keyboard,
)
from bot.states import RegistrationState, ScoreState

router = Router()


# ================== /start ==================


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""
    await state.clear()

    user = await api_client.get_user_by_telegram_id(str(message.from_user.id))

    if user:
        await state.update_data(user_id=user["id"])
        await message.answer(
            f"👋 Привет, {user['first_name']}!\n\nВыбери действие:",
            reply_markup=get_main_keyboard(),
        )
    else:
        await message.answer(
            "👋 Привет! Я бот для учёта баллов ЕГЭ.\n\n"
            "Для начала работы нужно зарегистрироваться.",
            reply_markup=get_start_keyboard(),
        )


# ================== /register ==================


@router.message(Command("register"))
@router.message(F.text == "📋 Зарегистрироваться")
async def cmd_register(message: Message, state: FSMContext):
    """Начало регистрации."""
    user = await api_client.get_user_by_telegram_id(str(message.from_user.id))
    if user:
        await state.update_data(user_id=user["id"])
        await message.answer(
            "✅ Вы уже зарегистрированы!", reply_markup=get_main_keyboard()
        )
        return

    await state.set_state(RegistrationState.waiting_first_name)
    await message.answer("📝 Введите ваше имя:", reply_markup=get_cancel_keyboard())


@router.message(RegistrationState.waiting_first_name, F.text == "❌ Отмена")
@router.message(RegistrationState.waiting_last_name, F.text == "❌ Отмена")
async def cancel_registration(message: Message, state: FSMContext):
    """Отмена регистрации."""
    await state.clear()
    await message.answer("❌ Регистрация отменена.", reply_markup=get_start_keyboard())


@router.message(RegistrationState.waiting_first_name)
async def process_first_name(message: Message, state: FSMContext):
    """Обработка имени."""
    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegistrationState.waiting_last_name)
    await message.answer("📝 Введите вашу фамилию:", reply_markup=get_cancel_keyboard())


@router.message(RegistrationState.waiting_last_name)
async def process_last_name(message: Message, state: FSMContext):
    """Обработка фамилии и создание пользователя."""
    data = await state.get_data()
    first_name = data.get("first_name", "")
    last_name = message.text.strip()
    full_name = f"{first_name} {last_name}"

    user = await api_client.create_user(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        telegram_id=str(message.from_user.id),
    )

    await state.clear()
    await state.update_data(user_id=user["id"])

    await message.answer(
        f"✅ Регистрация завершена!\n\nДобро пожаловать, {full_name}!",
        reply_markup=get_main_keyboard(),
    )


# ================== Выбор предмета ==================


@router.message(Command("select_subject"))
@router.message(F.text == "📚 Выбрать предмет")
async def cmd_select_subject(message: Message, state: FSMContext):
    """Выбор предмета."""
    user = await api_client.get_user_by_telegram_id(str(message.from_user.id))
    if not user:
        await message.answer(
            "⚠️ Сначала зарегистрируйтесь.", reply_markup=get_start_keyboard()
        )
        return

    await state.update_data(user_id=user["id"])
    await state.set_state(ScoreState.waiting_subject)
    await message.answer("📚 Выберите предмет:", reply_markup=get_subjects_keyboard())


@router.message(ScoreState.waiting_subject, F.text == "❌ Отмена")
async def cancel_subject_selection(message: Message, state: FSMContext):
    """Отмена выбора предмета."""
    await state.set_state(None)
    await message.answer("❌ Выбор предмета отменён.", reply_markup=get_main_keyboard())


@router.message(ScoreState.waiting_subject, F.text.in_(SUBJECTS))
async def process_subject(message: Message, state: FSMContext):
    """Обработка выбора предмета."""
    subject = message.text
    await state.update_data(subject=subject)
    await state.set_state(ScoreState.waiting_score)

    await message.answer(
        f"📝 Предмет: <b>{subject}</b>\n\nВведите балл (0-100):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(ScoreState.waiting_score, F.text == "❌ Отмена")
async def cancel_score_input(message: Message, state: FSMContext):
    """Отмена ввода балла."""
    await state.set_state(None)
    await message.answer("❌ Ввод балла отменён.", reply_markup=get_main_keyboard())


@router.message(ScoreState.waiting_score)
async def process_score(message: Message, state: FSMContext):
    """Обработка ввода балла."""
    try:
        score = int(message.text.strip())
        if not 0 <= score <= 100:
            raise ValueError("Score out of range")
    except ValueError:
        await message.answer("⚠️ Введите число от 0 до 100:")
        return

    data = await state.get_data()
    user_id = data.get("user_id")
    subject = data.get("subject")

    await api_client.create_object(
        name=subject,
        point=score,
        user_id=user_id,
    )

    await state.set_state(None)
    await message.answer(
        f"✅ Сохранено!\n\n📚 {subject}: {score} баллов",
        reply_markup=get_main_keyboard(),
    )


# ================== /view_scores ==================


@router.message(Command("view_scores"))
@router.message(F.text == "📊 Мои баллы")
async def cmd_view_scores(message: Message, state: FSMContext):
    """Просмотр всех баллов."""
    user = await api_client.get_user_by_telegram_id(str(message.from_user.id))
    if not user:
        await message.answer(
            "⚠️ Сначала зарегистрируйтесь.", reply_markup=get_start_keyboard()
        )
        return

    objects = await api_client.get_objects_by_user_id(user["id"])

    if not objects:
        text = "📭 У вас пока нет сохранённых баллов.\n\nИспользуйте «📚 Выбрать предмет» для добавления."
    else:
        lines = ["📊 <b>Ваши баллы:</b>\n"]
        for obj in objects:
            lines.append(f"• {obj['name']}: <b>{obj['point']}</b>")
        text = "\n".join(lines)

    await message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard())
