from datetime import datetime

from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import FromDishka

from repositories.feedbacks import FeedbackRepository
from services import UserService
from repositories import StreamRepository
from dtos import ChooseStreams, StreamDto, StreamDtoDB
from keyboards.feedback import feedback_kb

router = Router()


class FeedbackStates(StatesGroup):
    pending = State()


@router.message(Command('leave_feedback'))
async def leave_feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackStates.pending)
    await message.reply(
        'Оставьте ваши комментарии',
        reply_markup=feedback_kb()
    )


@router.callback_query(F.data == 'cancel_leave_feedback')
async def cancel_leave_feedback(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.clear()


@router.message(F.text, FeedbackStates.pending)
async def receive_feedback(
        message: Message,
        state: FSMContext,
        repo: FromDishka[FeedbackRepository]
):
    await state.clear()
    try:
        await repo.add_feedback(message.from_user.id, message.text)
        await message.reply('Спасибо за ваш отзыв!')
    except Exception as exc:
        print('----\n', exc, datetime.now(), '\n----')
        await message.reply('Что-то пошло не так. Напишите админу :)')
