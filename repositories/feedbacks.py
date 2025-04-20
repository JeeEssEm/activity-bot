from .base import BaseRepository
import models


class FeedbackRepository(BaseRepository):
    async def add_feedback(self, tg_id: int, content: str):
        feedback = models.Feedback(telegram_id=tg_id, content=content)
        self.session.add(feedback)
        await self.session.commit()
