from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

__all__ = (
    "BaseIDModel",
    "Base",
)


class BaseIDModel:

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, index=True, server_default=func.now())
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
