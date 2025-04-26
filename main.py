import asyncio
from datetime import datetime, UTC
import pathlib

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger

from dishka import make_async_container, FromDishka
from dishka.integrations.aiogram import setup_dishka

from schedule.job_wrappers import collect_schedule_wrapper
from shared import APIProvider, ServiceProvider, DatabaseProvider, serialize_dataclasses, deserialize_dataclasses
from config import settings, get_database_url, Database, get_job_storage_url, get_redis_url
from handlers import user_router, stream_router, activity_router, feedback_router, notification_router


def setup_scheduler() -> AsyncIOScheduler:
    executors = {'default': AsyncIOExecutor()}
    scheduler = AsyncIOScheduler(
        executors=executors,
        timezone=UTC,
    )

    return scheduler


def setup_redis() -> RedisStorage:
    return RedisStorage.from_url(
        get_redis_url(),
        json_loads=deserialize_dataclasses,
        json_dumps=serialize_dataclasses,
    )


async def main():
    scheduler = setup_scheduler()
    redis = setup_redis()
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),

    )
    dp = Dispatcher(storage=redis)

    providers = [
        APIProvider(),
        DatabaseProvider(get_database_url()),
        ServiceProvider(),
    ]

    container = make_async_container(*providers)
    setup_dishka(container, dp, auto_inject=True)

    async with container() as cont:
        await (await cont.get(Database)).check_and_create_tables()

    dp.include_router(user_router)
    dp.include_router(stream_router)
    dp.include_router(activity_router)
    dp.include_router(feedback_router)
    dp.include_router(notification_router)

    scheduler.add_job(
        collect_schedule_wrapper,
        trigger=CronTrigger(hour=6, timezone=UTC),
        id='collect_schedule',
        kwargs={
            'scheduler': scheduler,
            'container': container,
            'bot': bot,
        },
        next_run_time=datetime.now(tz=UTC)
    )
    scheduler.start()
    print('polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
