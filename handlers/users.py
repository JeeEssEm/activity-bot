from aiogram import types, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from dishka.integrations.aiogram import FromDishka

from repositories import UserRepository
from hse_api import HseAPI
from services import UserService


class UserStates(StatesGroup):
    waiting_for_email = State()
    choose_streams = State()


class UserHandler:
    command = 'start'

    @staticmethod
    async def start(message: types.Message, state: FSMContext):
        await message.reply('Введите вашу корпоративную почту:')
        await state.set_state(UserStates.waiting_for_email)

    @staticmethod
    async def process_email(
            message: types.Message,
            state: FSMContext,
            user_service: FromDishka[UserService],
    ):
        resp = await user_service.create(message.text, message.from_user.id)
        if resp.ok:
            await state.set_state(UserStates.choose_streams)
            # await state.clear()
        await message.reply(resp.msg)

    @staticmethod
    async def process_streams(
            message: types.Message,
            state: FSMContext,
            user_service: FromDishka[UserService],
    ):
        email = await user_service.get_user_email_by_id(message.from_user.id)
        resp = await user_service.get_streams(email)

        if resp.ok:
            msg = '\n'.join(resp.data)
            await message.reply(resp.msg + f'\n{msg}')


def register_user_handler(dp: Dispatcher):
    dp.message.register(UserHandler.start, Command(UserHandler.command))
    dp.message.register(UserHandler.process_email, StateFilter(UserStates.waiting_for_email))
    dp.message.register(UserHandler.process_streams, StateFilter(UserStates.choose_streams))
