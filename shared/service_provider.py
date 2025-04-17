from dishka import Provider, Scope, provide

from hse_api import HseAPI
from services import UserService, ActivityService
from repositories import UserRepository, StreamRepository, ActivityRepository


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

    @provide(scope=Scope.REQUEST)
    def provide_activity_service(self, activity_repo: ActivityRepository) -> ActivityService:
        return ActivityService(activity_repo=activity_repo)
