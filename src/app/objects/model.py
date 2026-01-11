from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.base.model import Base, BaseIDModel


class ObjectBase:
    name = Column(String(50), nullable=False)
    point = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Object(BaseIDModel, ObjectBase, Base):
    __tablename__ = "objects"

    user = relationship("User", back_populates="objects", lazy="select")
