import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dishka import make_async_container, FromDishka
from dishka.integrations.aiogram import setup_dishka

from shared import APIProvider, ServiceProvider, DatabaseProvider
from config import settings, get_database_url, Database
from handlers import register_user_handler


async def init_db(db: FromDishka[Database] = None):
    await db.init_models()


async def main():
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

    async with container() as cont:
        await init_db(await cont.get(Database))
    register_user_handler(dp)
    print('polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
