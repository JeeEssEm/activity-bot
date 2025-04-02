import asyncio

from repositories import UserRepository, StreamRepository
from config import Database, get_database_url


async def main():
    db = Database(get_database_url())
    # await db.init_models()
    async with db.session() as session:
        repo = StreamRepository(session)
        user_repo = UserRepository(session)
        user = await user_repo.create('asdf', 'asdf', 123)

        streams = await repo.create_streams_if_not_exists(['asdf', 'gfg'])
        await repo.create_streams_user(user.id, [streams[0].id, streams[1].id])
        # await repo.create_streams_user(user.id, [streams[0].id])

        print(await repo.get_user_streams(user.id))
        # print(streams)
        # await repo.create_stream_user()
        # res = await repo.get_user_streams(1)
        # for act in res:
        #     print(act)

        # repo = UserRepository(session)
        # await repo.create('asdf', 'asdf', 123)
        # await repo.get_user_name(123)


    # for mail in ['grsemorozov@edu.hse.ru', 'a.romanov@hse.ru', 'romashikhin.m.y@hse.ru']:
    #     service = await get_user_service().__anext__()
    #     print(await service.create(mail))


if __name__ == '__main__':
    asyncio.run(main())
