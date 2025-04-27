from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, relationship, mapped_column

if TYPE_CHECKING:
    from .users import User
    from .streams import Stream

from config import Base
from dtos import ActivityDto


class Activity(Base):
    __tablename__ = 'activities'
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    stream_id: Mapped[int] = mapped_column(
        ForeignKey('streams.id'),
        primary_key=True
    )
    activities: Mapped[int]
    notify: Mapped[bool] = mapped_column(default=True)

    user: Mapped['User'] = relationship()
    stream: Mapped['Stream'] = relationship(back_populates='activities')

    def convert_to_dto(self) -> ActivityDto:
        return ActivityDto(
            user_id=self.user_id,
            stream_id=self.stream_id,
            score=self.activities,
            notify=self.notify
        )
