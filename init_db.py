import asyncio

from config import Database, get_database_url



async def main():
    db = Database(get_database_url())
    await db.init_models()


if __name__ == '__main__':
    asyncio.run(main())
