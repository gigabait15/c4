from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_db
from src.app.users.crud import user_crud
from src.app.users.schema import UserCreate, UserRead

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/telegram/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id(telegram_id: str, db: AsyncSession = Depends(get_db)):
    """Получить пользователя по Telegram ID."""
    user = await user_crud.get_user_by_telegram_id(db, telegram_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить пользователя по ID."""
    user = await user_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserRead.model_validate(user)


@router.post("/", response_model=UserRead)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создать пользователя."""
    user = await user_crud.create(db, obj_in=user_in)
    return UserRead.model_validate(user)
