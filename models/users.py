from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

if TYPE_CHECKING:
    from .activities import Activity
from config import Base


class User(Base):
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(String(320), unique=True)
    fullname: Mapped[str] = mapped_column(String(244))

    activities: Mapped[list['Activity']] = relationship()
