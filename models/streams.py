from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .activities import Activity

from config import Base
from dtos import StreamDtoDB


class Stream(Base):
    __tablename__ = 'streams'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), unique=True)
    type: Mapped[str] = mapped_column(String(256))

    activities: Mapped[list['Activity']] = relationship()

    def convert_to_dto(self) -> StreamDtoDB:
        return StreamDtoDB(
            id=self.id,
            full_stream=self.title,
            type=self.type
        )
