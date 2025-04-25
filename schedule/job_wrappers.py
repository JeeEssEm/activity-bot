from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer

from .notifier import collect_schedule
from services import UserService
from repositories import ActivityRepository


async def collect_schedule_wrapper(
        scheduler: AsyncIOScheduler,
        container: AsyncContainer,
        bot: Bot
):
  async with container() as req:
      await collect_schedule(
          users_service=await req.get(UserService),
          activity_repo=await req.get(ActivityRepository),
          scheduler=scheduler,
          bot=bot
      )
