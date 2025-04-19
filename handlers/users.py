from re import compile, fullmatch
from datetime import datetime

from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart

from dishka.integrations.aiogram import FromDishka

from exceptions.hse_auth import (
    EmailAlreadyExistsInHseDB, EmailNotFoundInHseDB, InternalError
)
from repositories import UserRepository
from hse_api import HseAPI
from services import UserService
from keyboards.list_kb import build_start_choose_kb
from keyboards.discipline_kb import ensure_delete_kb
from dtos import ChooseStreams, StreamType
from constants import NAVIGATOR

router = Router()

validate_email = compile('^[a-z0-9](\\.?[a-z0-9]+)*@edu\\.hse\\.ru$')


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


@router.message(Command('delete_account'))
async def delete_account(
        message: types.Message,
):
    await message.reply(
        '❓Вы уверены, что хотите удалить этот аккаунт?❓\n'
        '❗Все данные об активностях будут удалены❗',
        reply_markup=ensure_delete_kb(
            yes_cb='confirm_delete_account',
            no_cb='cancel_delete_account',
        )
    )


@router.callback_query(F.data == 'confirm_delete_account')
async def confirm_delete_account(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[UserService],
):
    await cb.message.delete()
    try:
        await service.delete_user_by_id(cb.message.chat.id)
        await bot.send_message(
            chat_id=cb.message.chat.id,
            text='Аккаунт успешно удалён!'
        )
    except Exception as exc:
        print('----\n', exc, '\n', datetime.now(), cb.message.chat.id, '----\n')
        await bot.send_message(
            chat_id=cb.message.chat.id,
            text='Что-то пошло не так. Напишите админу'
        )

@router.callback_query(F.data == 'cancel_delete_account')
async def cancel_delete_account(
        cb: CallbackQuery
):
    await cb.message.delete()
