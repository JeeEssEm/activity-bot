import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger

from dishka import make_async_container, FromDishka
from dishka.integrations.aiogram import setup_dishka

from schedule import collect_schedule_wrapper
from shared import APIProvider, ServiceProvider, DatabaseProvider
from config import settings, get_database_url, Database, get_job_storage_url
from handlers import user_router, stream_router, activity_router, feedback_router, notification_router


def setup_scheduler() -> AsyncIOScheduler:
    executors = {'default': AsyncIOExecutor()}
    storages = {'default': SQLAlchemyJobStore(get_job_storage_url())}
    scheduler = AsyncIOScheduler(executors=executors, storages=storages)

    return scheduler


async def init_db(db: FromDishka[Database] = None):
    await db.init_models()


async def main():
    scheduler = setup_scheduler()
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    providers = [
        APIProvider(),
        DatabaseProvider(get_database_url()),
        ServiceProvider(),
    ]

    container = make_async_container(*providers)
    setup_dishka(container, dp, auto_inject=True)

    # async with container() as cont:
    #     await init_db(await cont.get(Database))

    dp.include_router(user_router)
    dp.include_router(stream_router)
    dp.include_router(activity_router)
    dp.include_router(feedback_router)
    dp.include_router(notification_router)

    # scheduler.add_job(
    #     collect_schedule_wrapper,
    #     trigger=CronTrigger(...), # TODO: сделать нормальный триггер
    #     id='collect_schedule',
    #     kwargs={
    #         'scheduler': scheduler,
    #         'container': container,
    #         'bot': bot,
    #     }
    # )
    # scheduler.start()
    print('polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
