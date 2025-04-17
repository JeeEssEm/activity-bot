from repositories import ActivityRepository


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo

    async def get_queue_by_stream_id(self, stream_id: int, user_id: int) -> str:
        queue = await self.activity_repo.get_queue_by_stream(stream_id=stream_id)

        msg = []
        for i, activity in enumerate(queue):
            if activity.user_id == user_id:
                msg.append(f'<b>{i + 1}. {activity.fullname} | Активностей: {activity.activities}</b>')
            else:
                msg.append(f'{i + 1}. {activity.fullname} | Активностей: {activity.activities}')
        return '\n'.join(msg)
