import asyncio
from urllib.parse import parse_qs, urlparse
from datetime import datetime

from jwt import decode
from aiohttp import ClientSession, FormData
from bs4 import BeautifulSoup


def get_token_exp(token: str):
    data = decode(token, options={
        'verify_signature': False
    })
    return datetime.fromtimestamp(data.get('exp'))


class HseAuth:
    def __init__(
            self,
            email: str, password: str,
            saml_url: str | None = None,
            api_url: str | None = None,
            refresh_token: str | None = None,
    ):
        self._email: str = email
        self._password: str = password
        self.saml: str = saml_url or 'https://saml.hse.ru/'
        self.api: str = api_url or 'https://api.hseapp.ru/'
        self.lock: asyncio.Lock = asyncio.Lock()
        self.headers: dict = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 8 '
                          'Build/AP4A.250205.002; wv) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Version/4.0 '
                          'Chrome/132.0.6834.164 Mobile Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Android '
                         'WebView";v="132"',
            'sec-ch-ua-mobile': '?1'
        }
        self._access_token_expires: datetime | None = None
        self._refresh_token_expires: datetime | None = None

        self._access_token: str | None = None
        self._refresh_token: str | None = None

        if refresh_token:
            self._refresh_token = refresh_token
            self._refresh_token_expires = get_token_exp(refresh_token)

    async def _sign_in(self, session: ClientSession, link: str) -> str:
        form_data = FormData()
        form_data.add_field('username', self._email)
        form_data.add_field('password', self._password)

        async with session.post(
                link, data=form_data, allow_redirects=False
        ) as resp:
            location = resp.headers.get('Location')
            query_params = parse_qs(urlparse(location).query)
        return query_params.get('code')

    async def _get_hse_app_tokens(self, session: ClientSession, code: str):
        link = self.saml + 'realms/hse/protocol/openid-connect/token'
        form_data = FormData()
        form_data.add_field('grant_type', 'authorization_code')
        form_data.add_field('client_id', 'app-x-android')
        form_data.add_field(
            'redirect_uri',
            'ru.hse.hseappx://saml.hse.ru/authorize_callback'
        )

        form_data.add_field('code', code)
        async with session.post(
                link, data=form_data, allow_redirects=False
        ) as resp:
            data = await resp.json()
            if data.get('error'):
                raise Exception('Указан неверный емейл или пароль!')
            self._set_tokens(data)

    async def _get_auth_session_link(self, session: ClientSession) -> str:
        link = self.saml + (
            'realms/hse/protocol/openid-connect/auth?client_id'
            '=app-x-android&response_type=code&'
            'redirect_uri=ru.hse.hseappx://saml.hse.ru/authorize_callback'
        )
        async with session.get(link) as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')

        form = soup.select_one('#kc-form-login')
        if not form:
            raise Exception('Что-то пошло не так в hse api...')
        return form.attrs.get('action')

    async def _login(self):
        async with ClientSession(headers=self.headers) as session:
            # получаем айди сессии от формы входа
            link = await self._get_auth_session_link(session)
            session.headers.add(
                'Content-Type',
                'application/x-www-form-urlencoded'
            )
            # входим в аккаунт и получаем code
            code = await self._sign_in(session, link)
            # идём за токенами для hse app x: ура!
            await self._get_hse_app_tokens(session, code)

    def _is_access_token_valid(self) -> bool:
        if self._access_token_expires is None:
            return False
        if datetime.now() > self._access_token_expires:
            return False
        return True

    def _is_refresh_token_valid(self) -> bool:
        if self._refresh_token_expires is None:
            return False
        if datetime.now() > self._refresh_token_expires:
            return False
        return True

    async def get_access_token(self) -> str:
        async with self.lock:
            if self._is_access_token_valid():
                return self._access_token
            await self.refresh_tokens()
            return self._access_token

    async def refresh_tokens(self):
        if not self._refresh_token or not self._is_refresh_token_valid():
            await self._login()
            return

        link = self.saml + 'realms/hse/protocol/openid-connect/token'
        async with ClientSession(headers=self.headers) as session:
            form = FormData()
            form.add_field('refresh_token', self._refresh_token)
            form.add_field('client_id', 'app-x-android')
            form.add_field('grant_type', 'refresh_token')
            async with session.post(link, data=form) as resp:
                data = await resp.json()
                if data.get('error'):
                    print(data)
                    raise Exception('Что-то пошло не так...')
                self._set_tokens(data)

    def _set_tokens(self, data: dict):
        self._access_token = data.get('access_token')
        self._refresh_token = data.get('refresh_token')

        self._access_token_expires = get_token_exp(self._access_token)
        self._refresh_token_expires = get_token_exp(self._refresh_token)
