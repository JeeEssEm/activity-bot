from dtos import UserDto
from models.users import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, email: str, fullname: str, tg_id: int):
        user = User(email=email, fullname=fullname, id=tg_id)
        self.session.add(user)
        await self.session.commit()

    async def get_user_by_id(self, user_id: int) -> UserDto:
        user = await self.session.get(User, user_id)
        if user:
            return user.convert_to_dto()
        raise Exception('Пользователь не найден!')

    async def user_exists_by_id(self, user_id: int) -> bool:
        user = await self.session.get(User, user_id)
        return not user

    async def user_exists_by_email(self, email: str) -> bool:
        user = await self.session.get(User, {'email': email})  # FIXME
        return not user
