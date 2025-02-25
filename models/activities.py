from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from .users import User
    from .streams import Stream

from config import Base


class Activity(Base):
    __tablename__ = 'activities'
    user_id: Mapped[int] = relationship()
    stream_id: Mapped[int] = relationship()
    activities: Mapped[int]

    user: Mapped['User'] = relationship(back_populates='activities')
    stream: Mapped['Stream'] = relationship(back_populates='activities')
