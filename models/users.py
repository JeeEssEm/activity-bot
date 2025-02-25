from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

if TYPE_CHECKING:
    from .activities import Activity
from dtos import UserDto
from config import Base


class User(Base):
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(String(320), unique=True)
    fullname: Mapped[str] = mapped_column(String(244))

    activities: Mapped[list['Activity']] = relationship()

    def convert_to_dto(self) -> UserDto:
        return UserDto(email=self.email, fullname=self.fullname)
