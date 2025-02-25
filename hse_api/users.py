import aiohttp

from .auth import HseAuth
from dtos import (
    UserDto, ScheduleDto, StreamsDto, StreamsResponse,
    UserResponse, ErrorCode, ScheduleResponse,

)


class HseAPI:
    def __init__(self, auth_manager: HseAuth):
        self._auth_manager = auth_manager
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 8 '
                          'Build/AP4A.250205.002; wv) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Version/4.0 '
                          'Chrome/132.0.6834.164 Mobile Safari/537.36'
        }

    async def get_user_info(self, email: str) -> UserResponse:
        token = await self._auth_manager.get_access_token()

        async with aiohttp.ClientSession(headers=self.headers) as session:
            session.headers.add(
                'Authorization', f'Bearer {token}'
            )
            async with session.get(
                    f'https://api.hseapp.ru/v3/dump/email/{email}'
            ) as response:
                res = UserResponse(
                    ok=True,
                    dto=UserDto(
                        fullname=await response.text(),
                        email=email,
                    ),
                    msg='всё ок!',
                )
                if response.status != 200:
                    res.ok = False

                json = await response.json()
                if json.get('error'):
                    if json['error']['name'] == 'SendCommandError':
                        res.msg = 'Емейл не найден. Повторите ввод'
                        res.error_code = ErrorCode.not_found.value
                    else:
                        res.msg = 'Произошла внутренняя ошибка. Напишите админу'
                        res.error_code = ErrorCode.internal.value
                        print(json)
                else:
                    res.dto.fullname = json.get('full_name')
            return res

    async def get_user_schedule(
            self, email: str, start_date: str, end_date: str
    ) -> ScheduleResponse:
        link = (
            f'https://api.hseapp.ru/v3/ruz/lessons'
            f'?start={start_date}&email={email}&end={end_date}'
        )
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(link) as response:
                data = await response.json()
                resp = ScheduleResponse(
                    ok=True,
                    msg='ок',
                    dto=ScheduleDto(data)
                )
                if data.get('error'):
                    resp.ok = False
                    if data['error']['name'] == 'StudentNotFound':
                        resp.error_code = ErrorCode.not_found.value
                        resp.msg = 'Студент не найден'
                    else:
                        resp.error_code = ErrorCode.internal.value
                        resp.msg = ('Произошла внутренняя ошибка.'
                                    ' Напишите админу')

                return resp

    async def get_user_streams(
            self, email: str, start_date: str, end_date: str
    ):
        schedule = await self.get_user_schedule(
            email, start_date, end_date
        )
        if not schedule.ok:
            return StreamsResponse(
                ok=False,
                msg=schedule.msg,
                dto=StreamsDto([])
            )
        streams = []
        for stream in schedule.dto.schedule:
            streams.append(
                stream.get('stream')
            )
        return StreamsResponse(
            ok=True,
            msg='Ваши потоки:',
            dto=StreamsDto(streams)
        )
