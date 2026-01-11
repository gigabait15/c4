from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    telegram_id: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    telegram_id: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    full_name: str
    telegram_id: str
