from dishka import Provider, Scope, provide

from hse_api import HseAPI
from services import UserService
from repositories import UserRepository, StreamRepository


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_service(
            self,
            user_repo: UserRepository,
            stream_repo: StreamRepository,
            api: HseAPI
    ) -> UserService:
        return UserService(
            user_repo=user_repo,
            stream_repo=stream_repo,
            api=api
        )
