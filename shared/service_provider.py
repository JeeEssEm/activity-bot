from dishka import Provider, Scope, provide

from hse_api import HseAPI
from services import UserService
from repositories import UserRepository


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_user_service(
            self,
            repo: UserRepository,
            api: HseAPI
    ) -> UserService:
        return UserService(repo, api)
