import asyncio
from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from keyboards.notification_kb import notification_kb
from dtos import Notification, ActivityInfo
from repositories import ActivityRepository
from services import UserService


async def collect_schedule(
        users_service: UserService,
        activity_repo: ActivityRepository,
        scheduler: AsyncIOScheduler,
        bot: Bot
):
    """
    Короче, тут происходит минимизация количества запросов в HSE api.
    Достигается это за счёт выделения потоков у каждого пользования и пометки о каждом потоке.
    Например, у пользователей есть одинаковый поток, который будет на следующий день
    """

    # вытаскиваем все пары на сегодня
    streams = await activity_repo.get_streams_to_check()
    checked = set()  # уже проверенные потоки
    stream_time: dict[str, list[datetime]] = {}  # поток: расписание
    time_notification: dict[datetime, list[Notification]] = {}  # время: уведомления

    for email, acts in streams.items():
        if any(act.full_stream not in checked for act in acts):
            user_schedule = await users_service.get_user_schedule_today(email)
            for tt in user_schedule:
                checked.add(tt.full_stream)
                if tt.full_stream not in stream_time:
                    stream_time[tt.full_stream] = [tt.time_end]
                elif tt.time_end not in stream_time[tt.full_stream]:
                    stream_time[tt.full_stream].append(tt.time_end)

        for act in acts:
            if act.full_stream in stream_time:
                for time in stream_time[act.full_stream]:
                    notification = Notification(
                        user_id=act.user_id,
                        message=f'Как прошла пара по дисциплине <i>{act.full_stream.split('#')[-1]}</i>?',
                        stream_id=act.stream_id
                    )
                    if time not in time_notification:
                        time_notification[time] = [notification]
                    else:
                        time_notification[time].append(notification)
            else:
                checked.add(act.full_stream)

    for time, nots in time_notification.items():
        scheduler.add_job(
            notify_users,
            trigger=DateTrigger(time),
            args=(bot, nots)
        )
        print(f'job added at {time}: {nots}')


async def notify(bot: Bot, msg: str, user_id: int, stream_id: int):
    await bot.send_message(
        user_id, msg, reply_markup=notification_kb(stream_id))


async def notify_users(bot: Bot, nots: list[Notification]):
    tasks = [
        asyncio.create_task(
            notify(
                bot, notification.message,
                notification.user_id, notification.stream_id
            )
        ) for notification in nots]
    await asyncio.gather(*tasks)
