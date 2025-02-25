from repositories import UserRepository
from hse_api import UserAPIManager


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create(self, email: str) -> str:
        resp = await UserAPIManager.get_user_info(email)
        if resp.ok:
            await self.user_repo.create(email=email, fullname=resp.dto.fullname)
        return resp.msg
