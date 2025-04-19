import asyncio

from dtos import StreamDto
from repositories import UserRepository, StreamRepository
from config import Database, get_database_url
from repositories.activities import ActivityRepository


async def main():
    db = Database(get_database_url('test_base'))
    await db.init_models()
    async with db.session() as session:
        repo = StreamRepository(session)
        user_repo = UserRepository(session)
        activity_repo = ActivityRepository(session)
        blinov = await user_repo.create('asdf', 'Блинов', 123)
        kumar = await user_repo.create('asdf123', 'Нурматов', 1234)
        artem = await user_repo.create('asdf123123', 'Ипатьев', 1235)

        streams = await repo.create_streams_if_not_exists([
            StreamDto(type='САПР', full_stream='М_АИП_Г#алгоритмизация'),
            StreamDto(type='МАТ', full_stream='М_МАТ_Г#матан'),
            StreamDto(type='ФИЗ', full_stream='М_ФИЗ_Г#физика'),
        ])
        stream_ids = list(map(lambda stream: stream.id, streams))

        await repo.create_streams_user(blinov.id, stream_ids)
        await repo.create_streams_user(kumar.id, stream_ids)
        await repo.create_streams_user(artem.id, stream_ids)

        await repo.set_user_activities(blinov.id, streams[0].id, 10)
        await repo.set_user_activities(blinov.id, streams[2].id, 5)
        await repo.set_user_activities(artem.id, streams[2].id, 10)
        await repo.set_user_activities(kumar.id, streams[0].id, 1)
        await repo.set_user_activities(kumar.id, streams[1].id, 50)

        # print(await repo.get_median_activity(streams[0].id))
        # print(await repo.get_median_activity(streams[1].id))
        # print(await repo.get_median_activity(streams[2].id))
        print(kumar.id)
        # for t in await activity_repo.get_queue_by_stream(streams[0].id):
        #     print(t.fullname, t.activities)
        await user_repo.delete_user_by_id(kumar.id)
        # await repo.create_streams_user(user.id, [streams[0].id])

        # print(await repo.get_user_streams(user.id))



    # for mail in ['grsemorozov@edu.hse.ru', 'a.romanov@hse.ru', 'romashikhin.m.y@hse.ru']:
    #     service = await get_user_service().__anext__()
    #     print(await service.create(mail))


if __name__ == '__main__':
    asyncio.run(main())
