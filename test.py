import asyncio

from repositories import UserRepository
from config import Database, get_database_url


async def main():
    db = Database(get_database_url())
    await db.init_models()
    async with db.session() as session:
        repo = UserRepository(session)
        await repo.create('asdf', 'asdf', 123)
        # await repo.get_user_name(123)


    # for mail in ['grsemorozov@edu.hse.ru', 'a.romanov@hse.ru', 'romashikhin.m.y@hse.ru']:
    #     service = await get_user_service().__anext__()
    #     print(await service.create(mail))


if __name__ == '__main__':
    asyncio.run(main())
