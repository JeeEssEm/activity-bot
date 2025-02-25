from dataclasses import dataclass

import aiohttp

from config import settings
from dtos import UserDto


@dataclass
class Response:
    ok: bool
    dto: UserDto
    msg: str


class UserAPIManager:

    @staticmethod
    async def get_user_info(email: str) -> Response:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://api.hseapp.ru/v3/dump/email/{email}',
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Authorization': settings.HSE_API_TOKEN
                    }
            ) as response:
                res = Response(
                    ok=True,
                    dto=UserDto(
                        fullname=await response.text(),
                        email=email,
                    ),
                    msg='всё ок!')
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
