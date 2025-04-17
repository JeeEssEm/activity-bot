from sqlalchemy import select
# from sqlalchemy.orm import

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
