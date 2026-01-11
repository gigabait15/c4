from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from core.base.model import Base, BaseIDModel


class UserBase:
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(100), nullable=False)
    telegram_id = Column(String(100), nullable=False)


class User(BaseIDModel, UserBase, Base):
    __tablename__ = "users"

    objects = relationship("Object", back_populates="user", lazy="select")
