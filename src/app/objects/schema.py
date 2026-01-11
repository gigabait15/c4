from pydantic import BaseModel, ConfigDict


class ObjectCreate(BaseModel):
    name: str
    point: int
    user_id: int


class ObjectUpdate(BaseModel):
    name: str
    point: int


class ObjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    point: int
    user_id: int
