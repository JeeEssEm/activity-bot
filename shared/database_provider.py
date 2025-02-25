from typing import AsyncIterable

from config import Database
from repositories import UserRepository

from dishka import Provider, Scope, provide


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
