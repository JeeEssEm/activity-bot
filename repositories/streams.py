from .base import BaseRepository
import models
from exceptions.db import UserNotFound, ActivityAlreadyExists

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError


class StreamRepository(BaseRepository):
    async def get_user_streams(self, user_id: int):
        q = select(models.Stream.title).where(
            models.Activity.user_id == user_id,
            models.Activity.stream_id == models.Stream.id
        )
        res = await self.session.scalars(q)
        return res.all()

    async def create_streams_if_not_exists(self, titles: list[str]):
        q = select(models.Stream).where(
            models.Stream.title.in_(titles),
        )
        existing_streams = list(await self.session.scalars(q))
        existing_titles = list(map(lambda x: x.title, existing_streams))
        streams_to_create = [t for t in titles if t not in existing_titles]

        if streams_to_create:
            streams_to_create = [
                models.Stream(title=t) for t in streams_to_create
            ]
            self.session.add_all(streams_to_create)

            try:
                await self.session.commit()
                res = await self.session.scalars(q)
                return list(res.all())
            except IntegrityError:
                raise ActivityAlreadyExists()
        return existing_streams

    async def create_streams_user(self, user_id: int, stream_ids: list[int]):
        activities = [models.Activity(
            user_id=user_id, stream_id=stream_id, activities=0
        ) for stream_id in stream_ids]
        self.session.add_all(activities)
        await self.session.commit()
