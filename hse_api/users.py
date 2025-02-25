from dataclasses import dataclass

import aiohttp

from .auth import HseAuth
from dtos import UserDto


@dataclass
class Response:
    ok: bool
    dto: UserDto
    msg: str


class HseAPI:
    def __init__(self, auth_manager: HseAuth):
        self._auth_manager = auth_manager
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 8 '
                          'Build/AP4A.250205.002; wv) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Version/4.0 '
                          'Chrome/132.0.6834.164 Mobile Safari/537.36'
        }

    async def get_user_info(self, email: str) -> Response:
        token = await self._auth_manager.get_access_token()
        print(self._auth_manager._access_token_expires)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            session.headers.add(
                'Authorization', f'Bearer {token}'
            )
            async with session.get(
                    f'https://api.hseapp.ru/v3/dump/email/{email}'
            ) as response:
                res = Response(
                    ok=True,
                    dto=UserDto(
                        fullname=await response.text(),
                        email=email,
                    ),
                    msg='всё ок!'
                )
                if response.status != 200:
                    res.ok = False

                json = await response.json()
                if json.get('error'):
                    if json.get('error') == 'SendCommandError':
                        res.msg = 'Емейл не найден'
                    else:
                        res.msg = 'Произошла внутренняя ошибка. Напишите админу'
                        print(json)
                else:
                    res.dto.fullname = json.get('full_name')
            return res

    async def get_user_streams(self, email: str):
        ...
