from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .activities import Activity

from config import Base


class Stream(Base):
    __tablename__ = 'streams'
    title: Mapped[str]

    activities: Mapped[list['Activity']] = relationship()

