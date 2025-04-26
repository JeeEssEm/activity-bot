from sqlalchemy import select, update, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from exceptions.db import CannotAddActivityToNotSubscribedStudent
from repositories.base import BaseRepository
import models
from dtos import ActivityInfo, QueueActivityElementDto, ActivityDto


class ActivityRepository(BaseRepository):
    async def get_queue_by_stream(self, stream_id: int) -> list[QueueActivityElementDto]:
        q = (select(models.User.id, models.User.fullname, models.Activity.activities)
             .where(models.Activity.stream_id == stream_id)
             .join(models.User, onclause=models.User.id == models.Activity.user_id)
             .order_by(models.Activity.activities.asc())
             )
        out = await self.session.execute(q)
        res = []
        for user_id, fullname, activities in out.all():
            res.append(QueueActivityElementDto(user_id, fullname, activities))
        return res

    async def change_all_activities(self, user_id: int, mute: bool = False):
        q = (update(models.Activity)
             .where(models.Activity.user_id == user_id)
             .values(notify=not mute)
             )
        await self.session.execute(q)
        await self.session.commit()

    async def change_mute_activity(self, user_id: int, stream_id: int):
        q = (update(models.Activity)
             .where(
            models.Activity.user_id == user_id,
            models.Activity.stream_id == stream_id
        )
             .values(notify=not_(models.Activity.notify))
             )
        await self.session.execute(q)
        await self.session.commit()

    async def get_streams_to_check(self) -> dict[str, list[ActivityInfo]]:
        q = (select(
            models.Activity.stream_id, models.Activity.user_id,
            models.Stream.title, models.User.email
        )
             .where(models.Activity.notify == True)
             .join(models.User, onclause=models.User.id == models.Activity.user_id)
             .join(models.Stream, onclause=models.Stream.id == models.Activity.stream_id)
             .order_by(models.Activity.user_id)
             )
        out = await self.session.execute(q)
        res = {}
        for s_id, u_id, title, email in out.all():
            if email in res:
                res[email].append(ActivityInfo(s_id, u_id, title))
            else:
                res[email] = [ActivityInfo(s_id, u_id, title)]
        return res

    async def _get_user_activity(self, user_id: int, stream_id: int) -> models.Activity:
        obj = await self.session.get(
            models.Activity, {
                'user_id': user_id, 'stream_id': stream_id
            })
        if obj is None:
            raise CannotAddActivityToNotSubscribedStudent()
        return obj

    async def get_user_stream_activity(self, user_id: int, stream_id: int) -> ActivityDto:
        activity = await self._get_user_activity(user_id, stream_id)
        return activity.convert_to_dto()

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
