from typing import Type

from sqlalchemy import select, insert, delete


from models import Activity
from .base import BaseRepository
import models
from exceptions.db import UserNotFound, StreamNotFound, CannotAddActivityToNotSubscribedStudent
from dtos import StreamDto, StreamDtoDB, ActivityDto


class StreamRepository(BaseRepository):
    async def get_user_streams(self, user_id: int) -> list[StreamDtoDB]:
        activities_q = select(models.Activity.stream_id).where(
            models.Activity.user_id == user_id
        )
        q = select(models.Stream).where(models.Stream.id.in_(activities_q))

        res = await self.session.scalars(q)
        return list(map(lambda s: s.convert_to_dto(), res.all()))

    async def create_streams_if_not_exists(
            self, streams: list[StreamDto]
    ) -> list[StreamDtoDB]:
        titles = [s.full_stream for s in streams]
        q = select(models.Stream).where(
            models.Stream.title.in_(titles),
        )
        existing_streams = list(await self.session.scalars(q))
        existing_titles = list(map(lambda x: x.title, existing_streams))
        streams_to_create = [
            s for s in streams if s.full_stream not in existing_titles
        ]

        if streams_to_create:
            streams_to_create = [
                models.Stream(title=t.full_stream, type=t.type)
                for t in streams_to_create
            ]
            self.session.add_all(streams_to_create)
            # print(streams_to_create)
            # try:
            await self.session.commit()
            res = await self.session.scalars(q)
            return list(map(lambda s: s.convert_to_dto(), res.all()))
            # except IntegrityError:
            #     raise ActivityAlreadyExists()
        return list(map(lambda s: s.convert_to_dto(), existing_streams))

    async def create_streams_user(self, user_id: int, stream_ids: list[int]):
        activities = [models.Activity(
            user_id=user_id, stream_id=stream_id, activities=0
        ) for stream_id in stream_ids]
        self.session.add_all(activities)
        await self.session.commit()

    async def get_stream_by_id(self, stream_id: int) -> StreamDtoDB:
        stream: models.Stream = await self.session.get(models.Stream, stream_id)
        if stream is None:
            raise StreamNotFound()
        return stream.convert_to_dto()

    async def delete_user_stream(self, user_id: int, stream_id: int):
        q = delete(models.Activity).where(
            models.Activity.user_id == user_id,
            models.Activity.stream_id == stream_id
        )
        await self.session.execute(q)
        await self.session.commit()
