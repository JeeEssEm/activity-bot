from sqlalchemy import delete

from dtos import UserDto
import models
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, email: str, fullname: str, tg_id: int) -> UserDto:
        user = models.User(email=email, fullname=fullname, id=tg_id)
        self.session.add(user)
        await self.session.commit()
        return user.convert_to_dto()

    async def get_user_by_id(self, user_id: int) -> UserDto:
        user = await self.session.get(models.User, user_id)
        if user:
            return user.convert_to_dto()
        raise Exception('Пользователь не найден!')

    async def user_exists_by_id(self, user_id: int) -> bool:
        user = await self.session.get(models.User, user_id)
        return bool(user)

    async def user_exists_by_email(self, email: str) -> bool:
        user = await self.session.get(models.User, {'email': email})  # FIXME
        return not user

    async def delete_user_by_id(self, user_id: int):
        user = await self.session.get(models.User, user_id)
        await self.session.delete(user)
        await self.session.commit()
