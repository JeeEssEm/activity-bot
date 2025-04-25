from typing import Callable, Awaitable
from random import choice

from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from dishka.integrations.aiogram import FromDishka

from services import UserService
from repositories import StreamRepository, ActivityRepository
from dtos import ChooseStreams, StreamDto, StreamDtoDB
from keyboards.list_kb import build_start_choose_kb
from keyboards.discipline_kb import build_discipline_kb
from constants import GOOD_STICKERS, BAD_STICKERS, NEUTRAL_STICKERS

router = Router()


class IncrementActivityStates(StatesGroup):
    set_activity = State()


@router.callback_query(F.data.startswith('increment_activity_1_'))
async def increment_activity_by_1(
        cb: CallbackQuery,
        repo: FromDishka[ActivityRepository]
):
    stream_id = int(cb.data.split('_')[-1])
    await repo.increment_user_activity(
        cb.from_user.id,
        stream_id
    )
    await cb.message.delete()
    await cb.message.answer_sticker(choice(GOOD_STICKERS))


@router.callback_query(F.data.startswith('increment_activity_n_'))
async def increment_activity_by_n(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext
):
    stream_id = int(cb.data.split('_')[-1])
    await state.set_state(IncrementActivityStates.set_activity)
    await state.update_data(stream_id=stream_id)

    await cb.message.delete()
    await bot.send_message(
        cb.from_user.id,
        'Введите зафармленное количество активностей'
    )


@router.callback_query(F.data == 'cancel_increment_activity')
async def cancel_increment_activity(
        cb: CallbackQuery,
        bot: Bot
):
    await cb.message.delete()
    await bot.send_sticker(
        cb.message.chat.id,
        choice(BAD_STICKERS),
    )


@router.message(F.text, IncrementActivityStates.set_activity)
async def confirm_increment_activity_by_n(
        msg: Message,
        state: FSMContext,
        repo: FromDishka[ActivityRepository]
):
    amount = msg.text.strip()
    state_data = await state.get_data()
    if not amount.isdigit() or not amount.isascii():
        await msg.answer('Количество активностей - это целое неотрицательное число! Повторите ввод')
        return
    amount = int(amount)
    if amount == 0:
        await msg.reply_sticker(choice(NEUTRAL_STICKERS))
        return
    elif amount < 0 or amount > 100:
        await msg.answer('Да не может оно быть отрицательным. И больше 100 тоже не может (тупо не верю в такое)')
        return
    await state.clear()
    await repo.increment_user_activity(
        msg.from_user.id,
        state_data.get('stream_id'),
        count=amount
    )
    await msg.reply_sticker(choice(GOOD_STICKERS))
