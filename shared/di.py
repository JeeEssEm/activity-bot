from typing import AsyncIterable

from dishka import Provider, Scope, provide

from config import settings, Database
from hse_api import HseAPI, HseAuth
from repositories import UserRepository


class AppProvider(Provider):

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


class DatabaseProvider(Provider):
    def __init__(self, database_url: str) -> None:
        self.db = Database(database_url)
        super().__init__()

    @provide(scope=Scope.APP)
    def provide_database(self) -> Database:
        return self.db

    @provide(scope=Scope.REQUEST)
    async def provide_user_repo(self) -> AsyncIterable[UserRepository]:
        async with self.db.session() as session:
            yield UserRepository(session)
