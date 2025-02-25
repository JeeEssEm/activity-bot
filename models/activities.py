from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

if TYPE_CHECKING:
    from .users import User
    from .streams import Stream

from config import Base


class Activity(Base):
    __tablename__ = 'activities'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    stream_id: Mapped[int] = mapped_column(ForeignKey('streams.id'))
    activities: Mapped[int]

    user: Mapped['User'] = relationship(back_populates='activities')
    stream: Mapped['Stream'] = relationship(back_populates='activities')
