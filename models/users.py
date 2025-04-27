from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger

if TYPE_CHECKING:
    from .activities import Activity
from dtos import UserDto
from config import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    fullname: Mapped[str] = mapped_column(String(244))

    activities: Mapped[list['Activity']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def convert_to_dto(self) -> UserDto:
        return UserDto(email=self.email, fullname=self.fullname, id=self.id)
