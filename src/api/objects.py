from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_db
from src.app.objects.crud import object_crud
from src.app.objects.schema import ObjectCreate, ObjectRead
from src.app.objects.service import ObjectService, object_service

router = APIRouter(
    prefix="/objects",
    tags=["objects"],
)


@router.get("/{user_id}", response_model=list[ObjectRead])
async def get_all_objects_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    objects = await object_crud.get_all_objects_by_user_id(db, user_id)
    return [ObjectRead.model_validate(obj) for obj in objects]


@router.post("/", response_model=ObjectRead)
async def create_new_object(
    object_in: ObjectCreate,
    service: ObjectService = Depends(object_service),
):
    obj = await service.create_new_object(
        user_id=object_in.user_id, object_in=object_in
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Object already exists"
        )
    return ObjectRead.model_validate(obj)
