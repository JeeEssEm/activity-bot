from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from config import Base


class User(Base):
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(String(255), unique=True)
    fullname: Mapped[str] = mapped_column(String(255 - len('@edu.hse.ru')))
