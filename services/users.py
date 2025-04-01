from datetime import datetime, timedelta

from repositories import UserRepository
from hse_api import HseAPI
from exceptions.hse_auth import EmailNotFoundInHseDB, EmailAlreadyExistsInHseDB
from dtos import StreamsDto, StreamType, StreamDto


class UserService:
    def __init__(self, user_repo: UserRepository, api: HseAPI):
        self.user_repo: UserRepository = user_repo
        self.api: HseAPI = api

    async def create(self, email: str, tg_id: int):
        # if await self.user_repo.user_exists_by_email(email):
        #     raise EmailAlreadyExistsInHseDB('Такой емейл уже есть в бд!')
        resp = await self.api.get_user_info(email)
        await self.user_repo.create(
            email=resp.email, tg_id=tg_id, fullname=resp.fullname
        )

    async def get_user_email_by_id(self, tg_id: int):
        user = await self.user_repo.get_user_by_id(tg_id)
        return user.email

    async def get_streams(self, email: str) -> StreamsDto:
        today = datetime.today()
        raw_streams = await self.api.get_user_schedule(
            email,
            start_date=today.strftime('%Y-%m-%d'),
            end_date=(today + timedelta(days=30)).strftime('%Y-%m-%d')
        )
        uniq_streams = set(
            StreamDto(
                type=StreamType.from_string(s.get('type')),
                title=s.get('stream', '##').split('#')[-1],
                full_stream=s.get('stream')
            )
            for s in raw_streams.schedule
        )
        return StreamsDto(list(uniq_streams))

    async def user_exists(self, tg_id: int) -> bool:
        ...
