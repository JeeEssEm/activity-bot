import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from handlers import register_user_handler
from config import get_database_url, Database


async def init_db():
    db = Database(get_database_url())
    await db.init_models()


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    await init_db()
    register_user_handler(dp)
    print('polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
