from sqlalchemy.orm import Mapped, mapped_column

from config import Base


class Stream(Base):
    __tablename__ = 'streams'
    title: Mapped[str]
