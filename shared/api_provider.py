from typing import AsyncIterable

from dishka import Provider, Scope, provide

from config import settings, Database
from hse_api import HseAPI, HseAuth
from repositories import UserRepository


class APIProvider(Provider):

    @provide(scope=Scope.APP)
    def provide_auth_manager(self) -> HseAuth:
        if settings.HSE_REFRESH_TOKEN:
            return HseAuth(
                settings.HSE_EMAIL, settings.HSE_PASSWORD,
                refresh_token=settings.HSE_REFRESH_TOKEN
            )

        return HseAuth(settings.HSE_EMAIL, settings.HSE_PASSWORD)

    @provide(scope=Scope.APP)
    def provide_hse_api(self, hse_auth: HseAuth) -> HseAPI:
        return HseAPI(hse_auth)
