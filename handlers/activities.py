from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import FromDishka

from services import UserService
from repositories import StreamRepository
from dtos import ChooseStreams
from keyboards.list_kb import build_start_choose_kb
from keyboards.discipline_kb import build_discipline_kb, ensure_delete_kb
from .streams import show_my_disciplines

router = Router()


@router.callback_query(F.data.startswith('stop_tracking_'))
async def stop_tracking(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        repo: FromDishka[StreamRepository]
):
    stream_id = int(cb.data.split('_')[-1])
    stream = await repo.get_stream_by_id(stream_id)
    await cb.message.edit_text(
        text=f'Вы уверены, что хотите перестать отслеживать: {stream.title} {stream.type}'
    )
    await cb.message.edit_reply_markup(
        reply_markup=ensure_delete_kb(stream)
    )


@router.callback_query(F.data.startswith('confirm_stop_tracking_'))
async def stop_tracking(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        repo: FromDishka[StreamRepository],
        user_service: FromDishka[UserService]
):
    stream_id = int(cb.data.split('_')[-1])
    await repo.delete_user_stream(stream_id=stream_id, user_id=cb.message.chat.id)
    chosen_streams: ChooseStreams = (await state.get_data()).get('chosen_streams')
    chosen_streams.delete_stream_by_id(stream_id)

    await cb.message.delete()
    await bot.send_message(
        chat_id=cb.message.chat.id,
        text=f'Дисциплина больше не отслеживается!'
    )
    await state.clear()
    await show_my_disciplines(
        user_id=cb.from_user.id,
        state=state,
        send_func=lambda *args, **kwargs: cb.message.answer(*args, **kwargs),
        user_service=user_service
    )


@router.callback_query(F.data.startswith('queue_activity_'))
async def queue_activity(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[UserService]
):
    ...


@router.callback_query(F.data.startswith('set_activity_'))
async def set_activity(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[UserService]
):
    ...


