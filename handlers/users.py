from math import ceil

from aiogram import types, Dispatcher, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.filters.state import StateFilter

from dishka.integrations.aiogram import FromDishka

from exceptions.hse_auth import (
    EmailAlreadyExistsInHseDB, EmailNotFoundInHseDB, InternalError
)
from repositories import UserRepository
from hse_api import HseAPI
from services import UserService
from keyboards.list_kb import build_list_kb
from dtos import ChooseStreams, StreamType
from constants import LEGEND

router = Router()


class UserStates(StatesGroup):
    waiting_for_email = State()
    choose_streams = State()


@router.message(CommandStart())
async def start(
        message: types.Message,
        state: FSMContext,
        repo: FromDishka[UserRepository]
):
    if await repo.user_exists_by_id(message.from_user.id):
        await message.answer('Выберите действие')
        return
    await message.reply('Введите вашу корпоративную почту:')
    await state.set_state(UserStates.waiting_for_email)


@router.message(F.text, UserStates.waiting_for_email)
async def process_email(
        message: types.Message,
        state: FSMContext,
        user_service: FromDishka[UserService],
):
    try:
        await user_service.create(message.text, message.from_user.id)
        await message.reply('Аккаунт успешно создан!')
        # await state.set_state(UserStates.choose_streams)
        data: ChooseStreams = await user_service.get_user_disciplines_kb(
            message.from_user.id
        )
        await state.clear()
        await state.update_data(chosen_streams=data)

        await message.reply(
            f'🗺️Навигатор по типам:{LEGEND}\n'
            f'📚<b>Твои дисциплины для отслеживания</b>',
            reply_markup=build_list_kb(
                pages=data.content,
                chosen=data.chosen_streams,
                page=0,
                page_cb='my_disciplines_page|'
            )
        )

    except EmailNotFoundInHseDB:
        await message.reply('Такой Email не найден в базе ВШЭ!')
    except EmailAlreadyExistsInHseDB:
        await message.reply('Пользователь с таким email уже существует!')
    except InternalError or Exception:
        await message.reply('Произошла внутренняя ошибка. Напишите админу')
