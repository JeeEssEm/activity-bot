from datetime import datetime, timedelta

from repositories import UserRepository
from hse_api import HseAPI
from dtos import ErrorCode, Status, DataStatus


class UserService:
    def __init__(self, user_repo: UserRepository, api: HseAPI):
        self.user_repo: UserRepository = user_repo
        self.api: HseAPI = api

    async def create(self, email: str, tg_id: int) -> Status:
        if await self.user_repo.user_exists_by_email(email):
            return Status(
                False,
                'Пользователь с таким email уже существует!'
            )

        resp = await self.api.get_user_info(email)
        if resp.ok:
            await self.user_repo.create(
                email=resp.dto.email, tg_id=tg_id, fullname=resp.dto.fullname
            )
            return Status(
                True,
                'Аккаунт успешно создан!'
            )
        elif resp.error_code == ErrorCode.not_found.value:
            return Status(
                False,
                'Такой Email не найден в базе ВШЭ!'
            )

        return Status(
            False,
            'Произошла внутрення ошибка, напишите админу!'
        )

    async def get_user_email_by_id(self, tg_id: int):
        user = await self.user_repo.get_user_by_id(tg_id)
        return user.email

    async def get_streams(self, email: str):
        today = datetime.today()
        streams = await self.api.get_user_streams(
            email,
            start_date=today.strftime('%Y-%m-%d'),
            end_date=(today + timedelta(days=30)).strftime('%Y-%m-%d')
        )
        return DataStatus(
            ok=streams.ok,
            msg=streams.msg,
            data=streams.dto
        )

    async def user_exists(self, tg_id: int) -> bool:
        ...
