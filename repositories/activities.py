from sqlalchemy import select, update, not_

from repositories.base import BaseRepository
import models
from dtos import ActivityDto, StreamDtoDB, QueueActivityElementDto


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
            models.Activity.stream_id == stream_id)
             .values(notify=not_(models.Activity.notify))
             )
        await self.session.execute(q)
        await self.session.commit()
