from math import ceil
from datetime import datetime, timedelta

from repositories import UserRepository, StreamRepository
from hse_api import HseAPI
from exceptions.hse_auth import EmailNotFoundInHseDB, EmailAlreadyExistsInHseDB
from dtos import StreamsDto, StreamType, StreamDto, ChooseStreams
from keyboards.list_kb import build_list_kb


class UserService:
    def __init__(
            self,
            user_repo: UserRepository,
            stream_repo: StreamRepository,
            api: HseAPI
    ):
        self.user_repo: UserRepository = user_repo
        self.stream_repo: StreamRepository = stream_repo
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

    async def get_streams_from_api(self, email: str) -> StreamsDto:
        today = datetime.today()
        raw_streams = await self.api.get_user_schedule(
            email,
            start_date=today.strftime('%Y-%m-%d'),
            end_date=(today + timedelta(days=30)).strftime('%Y-%m-%d')
        )
        uniq_streams = set(
            StreamDto(
                type=s.get('type'),
                full_stream=s.get('stream'),
            )
            for s in raw_streams.schedule
        )
        return StreamsDto(list(uniq_streams))

    async def add_streams(self, user_id: int, streams: list[StreamDto]):
        streams = await self.stream_repo.create_streams_if_not_exists(streams)
        await self.stream_repo.create_streams_user(
            user_id,
            [s.id for s in streams]
        )

    async def user_exists(self, tg_id: int) -> bool:
        ...

    async def get_user_disciplines_kb(
            self, user_id: int, from_db: bool = False
    ) -> ChooseStreams:
        active_streams = []
        if from_db:
            active_streams = await self.stream_repo.get_user_streams(user_id)
            active_streams = [s.full_stream for s in active_streams]

        email = await self.get_user_email_by_id(user_id)
        streams = await self.get_streams_from_api(email)

        items_per_page = 5
        pages = [[] for _ in range(ceil(len(streams.streams) / items_per_page))]
        chosen = {}
        for i, stream in enumerate(streams.streams):
            pages[i // items_per_page].append(stream)
            chosen[stream.short_stream] = [
                stream.full_stream in active_streams,
                stream
            ]
        return ChooseStreams(pages, chosen)
