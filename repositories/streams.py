from typing import Type

from sqlalchemy import select, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

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

    async def _get_user_activity(self, user_id: int, stream_id: int) -> models.Activity:
        obj = await self.session.get(
            models.Activity, {
                'user_id': user_id, 'stream_id': stream_id
            })
        if obj is None:
            raise CannotAddActivityToNotSubscribedStudent()
        return obj

    # region TODO: вынести в ActivityRepository
    async def get_user_stream_activity(self, user_id: int, stream_id: int) -> float:
        user = await self._get_user_activity(user_id, stream_id)
        return user.activities

    async def set_user_activities(self, user_id: int, stream_id: int, activities: int):
        user = await self._get_user_activity(user_id, stream_id)
        user.activities = activities
        await self.session.commit()

    async def increment_user_activity(self, user_id: int, stream_id: int, count: int = 1):
        user = await self._get_user_activity(user_id, stream_id)
        user.activities += count
        await self.session.commit()

    async def get_median_activity(self, stream_id: int) -> float:
        filtered_activities = (
            select(models.Activity.activities)
            .where(models.Activity.stream_id == stream_id)
            .order_by(models.Activity.activities)
            .cte('filtered_activities'))
        numbered_activities = select(
            filtered_activities.c.activities,
            func.row_number().over(order_by=filtered_activities.c.activities).label('num'),
            func.count().over().label('total')
        ).cte('numbered_activities')

        median = (select(func.avg(numbered_activities.c.activities))
        .where(
            numbered_activities.c.num.in_(
                [
                    func.ceil((numbered_activities.c.total + 1) / 2),
                    func.floor((numbered_activities.c.total + 1) / 2)
                ]
            )
        ))
        return await self.session.scalar(median)
    # end region

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
