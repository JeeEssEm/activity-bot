from typing import Callable
from math import ceil
from datetime import datetime, timedelta

from repositories import UserRepository, StreamRepository
from hse_api import HseAPI
from exceptions.hse_auth import EmailNotFoundInHseDB, EmailAlreadyExistsInHseDB
from dtos import StreamsDto, StreamType, StreamDto, ChooseStreams, StreamDtoDB, TimeTableDTO


class UserService:
    ITEMS_PER_PAGE = 5

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

    async def get_streams_from_api(self, email: str) -> list[StreamDto]:
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
            for s in raw_streams.schedule if s.get('stream')
        )
        return list(uniq_streams)

    async def get_user_schedule_today(self, email: str) -> list[TimeTableDTO]:
        today = (datetime.today()).strftime('%Y-%m-%d')
        raw_streams = await self.api.get_user_schedule(
            email,
            start_date=today,
            end_date=today
        )
        res = []
        for subject in raw_streams.schedule:
            if subject.get('stream'):
                res.append(TimeTableDTO(
                    full_stream=subject['stream'],
                    time_end=datetime.fromisoformat(subject['date_end'])
                ))

        # mock data example
        # res = [
        #     TimeTableDTO(
        #         full_stream='М_МА_Г_859408_8#Г#Математический анализ',
        #         # time_end=datetime(2025, 4, 26, 15, 30), tzinfo=timezone('UTC'))
        #         time_end=datetime.fromisoformat('2025-04-26T12:36:00Z')
        #     )
        # ]
        return res

    async def add_streams(self, user_id: int, streams: list[StreamDto]):
        streams = await self.stream_repo.create_streams_if_not_exists(streams)
        await self.stream_repo.create_streams_user(
            user_id,
            [s.id for s in streams]
        )

    async def user_exists(self, tg_id: int) -> bool:
        return  await self.user_repo.user_exists_by_id(tg_id)

    async def get_active_user_disciplines(
            self, user_id: int
    ) -> (list[list[StreamDtoDB]], dict[bool, StreamDtoDB]):
        streams = await self.stream_repo.get_user_streams(user_id)
        pages, chosen = self.build_pages(
            streams, self.ITEMS_PER_PAGE,
            check_active=lambda _: False,
            get_key=lambda stream: stream.short_stream
        )
        return pages, chosen

    @staticmethod
    def build_pages(
            collection: list, items_per_page: int,
            check_active: Callable, get_key: Callable
    ) -> (list[list], dict):
        pages = [[] for _ in range(ceil(len(collection) / items_per_page))]
        chosen = {}
        for i, element in enumerate(collection):
            pages[i // items_per_page].append(element)
            chosen[get_key(element)] = [
                check_active(element),
                element
            ]
        return pages, chosen

    async def get_user_disciplines(
            self, user_id: int, from_db: bool = False
    ) -> ChooseStreams:
        active_streams = []
        if from_db:
            active_streams = await self.stream_repo.get_user_streams(user_id)
            active_streams = [s.full_stream for s in active_streams]

        email = await self.get_user_email_by_id(user_id)
        streams = await self.get_streams_from_api(email)

        pages, chosen = self.build_pages(
            streams, self.ITEMS_PER_PAGE,
            check_active=lambda stream: stream.full_stream in active_streams,
            get_key=lambda stream: stream.short_stream
        )
        return ChooseStreams(pages, chosen)

    async def get_unselected_user_disciplines(self, user_id: int) -> ChooseStreams:
        streams_from_db = set(await self.stream_repo.get_user_streams(user_id))
        email = await self.get_user_email_by_id(user_id)
        streams_from_api = set(await self.get_streams_from_api(email))

        streams_from_api -= streams_from_db
        pages, chosen = self.build_pages(
            list(streams_from_api), self.ITEMS_PER_PAGE,
            check_active=lambda _: False,
            get_key=lambda stream: stream.short_stream
        )
        return ChooseStreams(pages, chosen)

    async def delete_user_by_id(self, user_id: int):
        await self.user_repo.delete_user_by_id(user_id)
