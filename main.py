import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from shared import AppProvider
from config import settings, get_database_url, Database
from handlers import register_user_handler


async def init_db():
    db = Database(get_database_url())
    await db.init_models()


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    container = make_async_container(AppProvider())
    setup_dishka(container, dp, auto_inject=True)

    await init_db()
    register_user_handler(dp)
    print('polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
