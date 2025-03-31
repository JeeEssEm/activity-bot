from aiogram import types, Dispatcher, Router, F
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import FromDishka

from services import UserService

router = Router()


@router.message(F.text == 'Мои дисциплины')
async def get_all_streams(
        message: types.Message,
        state: FSMContext,
        service: FromDishka[UserService]
):
    email = await service.get_user_email_by_id(message.from_user.id)
    streams = await service.get_streams(email)
    # ответ юзеру в виде всех его потоков
