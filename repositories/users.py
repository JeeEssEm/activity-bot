from models.users import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, email: str, fullname: str):
        user = User(email=email, fullname=fullname)
        self.session.add(user)
        await self.session.commit()
