from re import compile, fullmatch

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
from keyboards.list_kb import build_start_choose_kb
from dtos import ChooseStreams, StreamType
from constants import NAVIGATOR

router = Router()

validate_email = compile('^[a-z0-9](\\.?[a-z0-9])@edu\\.hse\\.ru$')


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
        email = message.text
        if validate_email.match(email):
            await user_service.create(email, message.from_user.id)
            await message.reply('Аккаунт успешно создан!')
            data: ChooseStreams = await user_service.get_user_disciplines(
                message.from_user.id
            )
            await state.clear()
            await state.update_data(chosen_streams=data)

            await message.reply(
                f'Теперь выберете дисциплины для отслеживания\n'
                f'{NAVIGATOR}',
                reply_markup=build_start_choose_kb(
                    pages=data.content,
                    chosen=data.chosen_streams,
                    page=0,
                    page_cb='my_disciplines_page|'
                )
            )
        else:
            await message.reply(
                'Email указан в некорректном формате! Он должен быть в формате <i>&lt;адрес&gt;@edu.hse.ru</i>'
            )

    except EmailNotFoundInHseDB:
        await message.reply('Такой Email не найден в базе ВШЭ!')
    except EmailAlreadyExistsInHseDB:
        await message.reply('Пользователь с таким email уже существует!')
    except InternalError or Exception:
        await message.reply('Произошла внутренняя ошибка. Напишите админу')
