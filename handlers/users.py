from aiogram import types, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from dishka.integrations.aiogram import FromDishka

from hse_api import HseAPI


class UserStates(StatesGroup):
    waiting_for_email = State()


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
            api: FromDishka[HseAPI],
    ):
        data = await api.get_user_info(message.text)
        if data.ok:
            await message.reply(f'Ваше ФИО: {data.dto.fullname}')
        else:
            await message.reply(f'{data}')
        await state.clear()


def register_user_handler(dp: Dispatcher):
    dp.message.register(UserHandler.start, Command(UserHandler.command))
    dp.message.register(UserHandler.process_email, StateFilter(UserStates.waiting_for_email))
