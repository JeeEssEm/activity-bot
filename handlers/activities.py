import datetime as dt

from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from dishka.integrations.aiogram import FromDishka

from services import UserService, ActivityService
from repositories import StreamRepository, ActivityRepository
from dtos import ChooseStreams, StreamDtoDB
from keyboards.list_kb import build_start_choose_kb
from keyboards.discipline_kb import build_discipline_kb, ensure_delete_kb, change_activities
from .streams import show_my_disciplines, show_subject_details

router = Router()

class ActivityState(StatesGroup):
    setting = State()


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


@router.callback_query(F.data == 'confirm_stop_tracking')
async def stop_tracking(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        repo: FromDishka[StreamRepository],
        user_service: FromDishka[UserService]
):
    state_data = await state.get_data()
    stream: StreamDtoDB = state_data.get('current_stream')
    await repo.delete_user_stream(stream_id=stream.id, user_id=cb.message.chat.id)

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


@router.callback_query(F.data == 'queue_activity')
async def queue_activity(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[ActivityService]
):
    state_data = await state.get_data()
    stream = state_data.get('current_stream')
    queue = await service.get_queue_by_stream_id(stream.id, cb.from_user.id)
    current_time = dt.datetime.now().strftime('%d.%m.%Y %H:%M')
    await cb.message.reply(
        text=f'Очередь по дисциплине <b>{stream.title} ({stream.type})</b> на момент <b>{current_time}</b>\n'
             f'{queue}'
    )

@router.callback_query(F.data.startswith('set_activity_'))
async def set_activity(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[UserService]
):
    await state.set_state(ActivityState.setting)
    sent = await cb.message.reply(
        text='Введите ваше текущее количество активностей',
        reply_markup=change_activities()
    )
    await state.update_data(prev_msg_id=sent.message_id)

    await cb.message.delete()


@router.callback_query(F.data == 'cancel_set_activity')
async def cancel_set_activity(
    cb: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    stream_repo: FromDishka[StreamRepository],
):
    data = await state.get_data()
    stream: StreamDtoDB = data.get('current_stream')

    await cb.message.delete()
    await state.clear()

    await show_subject_details(
        user_id=cb.from_user.id,
        stream=stream,
        state=state,
        stream_repo=stream_repo,
        send_func=lambda *args, **kwargs: bot.send_message(cb.message.chat.id, *args, **kwargs)
    )


@router.message(F.text, ActivityState.setting)
async def set_activity(
        msg: Message,
        bot: Bot,
        state: FSMContext,
        repo: FromDishka[StreamRepository]
):
    amount = msg.text.strip()
    if not amount.isdigit():
        await msg.answer('Количество активностей - это целое неотрицательное число! Повторите ввод')
        return
    amount = int(amount)
    if amount > 10 * 247:
        await msg.answer(
            'Бля, не верю. Если ебашить по 10 активностей за семинар, который 5 раз на неделе,'
            ' то максимум получится 10 * 247 (количество рабочих дней в году) - потолок. Повторите ввод'
        )
        return
    state_data = await state.get_data()
    stream: StreamDtoDB = state_data.get('current_stream')
    prev_msg_id = state_data.get('prev_msg_id')
    await repo.set_user_activities(
        user_id=msg.from_user.id, stream_id=stream.id, activities=amount
    )
    await state.clear()

    await msg.answer('Количество активностей успешно изменено!')
    await bot.delete_message(chat_id=msg.chat.id, message_id=prev_msg_id)

    await show_subject_details(
        user_id=msg.from_user.id,
        stream=stream,
        state=state,
        stream_repo=repo,
        send_func=lambda *args, **kwargs: bot.send_message(msg.from_user.id, *args, **kwargs)
    )


@router.callback_query(F.data == 'cancel_delete_subject')
async def cancel_delete_discipline(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        repo: FromDishka[StreamRepository]
):
    await cb.message.delete()
    state_data = await state.get_data()
    stream: StreamDtoDB = state_data.get('current_stream')
    await show_subject_details(
        user_id=cb.from_user.id,
        stream=stream,
        state=state,
        stream_repo=repo,
        send_func=lambda *args, **kwargs: bot.send_message(cb.from_user.id, *args, **kwargs)
    )
