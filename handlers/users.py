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
from dtos import ChooseStreams, StreamType, StreamState

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
        await state.clear()
    except EmailNotFoundInHseDB:
        await message.reply('Такой Email не найден в базе ВШЭ!')
    except EmailAlreadyExistsInHseDB:
        await message.reply('Пользователь с таким email уже существует!')
    except InternalError or Exception:
        await message.reply('Произошла внутренняя ошибка. Напишите админу')


# @router.message(F.text, UserStates.choose_streams)
# async def process_streams(
#         message: types.Message,
#         state: FSMContext,
#         user_service: FromDishka[UserService],
# ):
#     email = await user_service.get_user_email_by_id(message.from_user.id)
#     streams = await user_service.get_streams(email)
#
#     msg = '\n'.join(streams.streams)
#     await message.reply(f'Вот ваши дисциплины:\n{msg}')


@router.message(Command('my_disciplines'))
async def get_disciplines(
        message: types.Message,
        state: FSMContext,
        user_service: FromDishka[UserService],
):
    email = await user_service.get_user_email_by_id(message.from_user.id)
    streams = await user_service.get_streams(email)

    items_per_page = 5
    pages = [[] for _ in range(ceil(len(streams.streams) / items_per_page))]
    chosen = {}
    for i, stream in enumerate(streams.streams):
        pages[i // items_per_page].append(stream)
        chosen[stream.short_stream] = StreamState(
            stream.full_stream,
            False
        )

    await state.update_data(chosen_streams=ChooseStreams(
        content=pages,
        chosen_streams=chosen,
    ))

    legend = f'''
├Лекция: {StreamType.lecture.value}
├Семинар: {StreamType.seminar.value}
├Практические занятия: {StreamType.practice.value}
╰Научно-исследовательский семинар: {StreamType.science_seminar.value}
    '''
    await message.reply(
        f'🗺️Навигатор по типам:{legend}\n'
        f'📚<b>Твои дисциплины для отслеживания</b>',
        reply_markup=build_list_kb(
            pages=pages,
            chosen=chosen,
            page=0,
            page_cb='my_disciplines_page|'
        )
    )
