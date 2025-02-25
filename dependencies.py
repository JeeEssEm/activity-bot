from config import Database
from services import UserService
from repositories import UserRepository
from config import get_database_url


async def get_user_service() -> UserService:
    db = Database(get_database_url())
    async with db.session() as session:
        repo = UserRepository(session)
        service = UserService(repo)
        yield service
