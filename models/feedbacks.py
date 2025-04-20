from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from config import Base


class Feedback(Base):
    __tablename__ = 'feedbacks'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int]
    content: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
