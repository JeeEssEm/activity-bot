import asyncio

from dependencies import get_user_service


async def main():
    for mail in ['grsemorozov@edu.hse.ru', 'a.romanov@hse.ru', 'romashikhin.m.y@hse.ru']:
        service = await get_user_service().__anext__()
        print(await service.create(mail))


if __name__ == '__main__':
    asyncio.run(main())
