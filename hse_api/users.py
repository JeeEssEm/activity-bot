import aiohttp

from .auth import HseAuth
from dtos import (
    UserDto, ScheduleDto, StreamsDto,
)
from exceptions.hse_auth import (
    EmailNotFoundInHseDB, InternalError
)
from exceptions.hse_api import StudentNotFound


class HseAPI:
    def __init__(self, auth_manager: HseAuth):
        self._auth_manager = auth_manager
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 8 '
                          'Build/AP4A.250205.002; wv) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Version/4.0 '
                          'Chrome/132.0.6834.164 Mobile Safari/537.36'
        }

    async def get_user_info(self, email: str) -> UserDto:
        token = await self._auth_manager.get_access_token()

        async with aiohttp.ClientSession(headers=self.headers) as session:
            session.headers.add(
                'Authorization', f'Bearer {token}'
            )
            async with session.get(
                    f'https://api.hseapp.ru/v3/dump/email/{email}'
            ) as response:
                res = UserDto(
                        fullname=await response.text(),
                        email=email,
                    )

                json = await response.json()
                if json.get('error'):
                    if json['error']['name'] == 'SendCommandError':
                        raise EmailNotFoundInHseDB(
                            'Емейл не найден. Повторите ввод'
                        )
                    else:
                        print(json)
                        raise InternalError(
                            'Произошла внутренняя ошибка. Напишите админу'
                        )
                else:
                    res.fullname = json.get('full_name')
            return res

    async def get_user_schedule(
            self, email: str, start_date: str, end_date: str
    ) -> ScheduleDto:
        link = (
            f'https://api.hseapp.ru/v3/ruz/lessons'
            f'?start={start_date}&email={email}&end={end_date}'
        )
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(link) as response:
                data = await response.json()
                resp = ScheduleDto(data)

                if isinstance(data, dict) and data.get('error'):
                    if data['error']['name'] == 'StudentNotFound':
                        raise StudentNotFound('Студент не найден')
                    else:
                        raise InternalError(
                            'Произошла внутренняя ошибка. Напишите админу'
                        )

                return resp

    # async def get_user_streams(
    #         self, email: str, start_date: str, end_date: str
    # ) -> StreamsDto:
    #     schedule = await self.get_user_schedule(
    #         email, start_date, end_date
    #     )
    #     streams = []
    #     for stream in schedule.schedule:
    #         streams.append(
    #             stream.get('stream')
    #         )
    #     return StreamsDto(streams)
