from typing import Callable, Awaitable

from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import FromDishka

from services import UserService
from repositories import StreamRepository, ActivityRepository
from dtos import ChooseStreams, StreamDto, StreamDtoDB
from keyboards.list_kb import build_start_choose_kb
from keyboards.discipline_kb import build_discipline_kb
from constants import LEGEND, NAVIGATOR

router = Router()


async def show_my_disciplines(
        user_id: int,
        state: FSMContext,
        send_func: Callable[..., Awaitable[Message]],
        user_service: UserService
):
    pages, chosen = await user_service.get_active_user_disciplines(user_id)
    notification_buttons = [
                [('turn_off_all_notifications', '🔕Заглушить все уведомления')],
                [('turn_on_all_notifications', '🔔Включить все уведомления')]
            ]
    await state.update_data(
        chosen_streams=ChooseStreams(
            content=pages,
            chosen_streams=chosen
        ),
        confirm={
            'cb': 'my_disciplines_confirm',
            'text': '➕Добавить'
        },
        other_buttons=notification_buttons
    )

    await send_func(
        NAVIGATOR,
        reply_markup=build_start_choose_kb(
            pages, chosen,
            0,
            page_cb='my_disciplines_page|',
            confirm='➕Добавить',
            confirm_cb='my_disciplines_add',
            other_buttons=notification_buttons
        )
    )


async def show_subject_details(
    user_id: int,
    state: FSMContext,
    stream: StreamDtoDB,
    activity_repo: ActivityRepository,
    send_func: Callable[..., Awaitable[Message]]
):
    if not stream:
        await send_func('Ошибка: дисциплина не найдена.')
        return
    await state.update_data(current_stream=stream)
    median = await activity_repo.get_median_activity(stream.id)
    current_activity = await activity_repo.get_user_stream_activity(user_id, stream.id)

    await send_func(
        text=f'<b>{stream.title} ({stream.type})</b>\n'
             f'👤Ваша активность: {current_activity.score}\n'
             f'📈 Медианная активность: {median:.2f}\n',
        reply_markup=build_discipline_kb(stream.id, current_activity.notify)
    )


@router.callback_query(F.data.startswith('modify_subjs|'))
async def modify_list(
        cb: CallbackQuery,
        state: FSMContext
):
    state_data = await state.get_data()
    args = cb.data.split('|')
    title = args[-1]
    page = int(args[-2])
    data: ChooseStreams = state_data.get('chosen_streams')
    data.chosen_streams[title][0] = (
        not data.chosen_streams[title][0]
    )
    await state.update_data(chosen_streams=data)

    # confirm data
    confirm_cb = 'my_disciplines_confirm'
    confirm_text = 'Готово'
    confirm_data = state_data.get('confirm')
    if confirm_data is not None:
        confirm_cb = confirm_data.get('cb')
        confirm_text = confirm_data.get('text')
    # other buttons
    other_buttons = state_data.get('other_buttons')

    await cb.message.edit_reply_markup(
        reply_markup=build_start_choose_kb(
            pages=data.content, chosen=data.chosen_streams, page=page,
            page_cb='my_disciplines_page|',
            confirm_cb=confirm_cb, confirm=confirm_text,
            other_buttons=other_buttons
        )
    )


@router.callback_query(F.data.startswith('my_disciplines_page|'))
async def get_discipline_page(
        cb: CallbackQuery,
        state: FSMContext
):
    state_data = await state.get_data()

    # confirm data
    confirm_cb = 'my_disciplines_confirm'
    confirm_text = 'Готово'
    confirm_data = state_data.get('confirm')
    if confirm_data is not None:
        confirm_cb = confirm_data.get('cb')
        confirm_text = confirm_data.get('text')
    # other buttons
    other_buttons = state_data.get('other_buttons')

    data: ChooseStreams = state_data.get('chosen_streams')
    page = int(cb.data.split('|')[-1])

    await cb.message.edit_reply_markup(
        reply_markup=build_start_choose_kb(
            pages=data.content, chosen=data.chosen_streams, page=page,
            page_cb='my_disciplines_page|',
            confirm=confirm_text,
            confirm_cb=confirm_cb,
            other_buttons=other_buttons
        )
    )


@router.callback_query(F.data == 'my_disciplines_confirm')
async def confirm(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[UserService]
):
    data: ChooseStreams = (await state.get_data()).get('chosen_streams')
    await service.add_streams(
        user_id=cb.message.chat.id,
        streams=[s[1] for s in data.chosen_streams.values() if s[0]],
    )
    await cb.message.delete()
    await state.clear()
    await bot.send_message(
        chat_id=cb.message.chat.id,
        text='Дисциплины для отслеживания успешно изменены!'
    )

    await show_my_disciplines(
        user_id=cb.from_user.id,
        state=state,
        send_func=lambda text, reply_markup: bot.send_message(cb.from_user.id, text=text, reply_markup=reply_markup),
        user_service=service
    )


@router.message(Command('my_disciplines'))
async def get_my_disciplines(
        message: Message,
        state: FSMContext,
        user_service: FromDishka[UserService],
):
    if not await user_service.user_exists(message.from_user.id):
        await message.reply('Сначала зарегайтесь через /start')
        return

    await show_my_disciplines(
        user_id=message.from_user.id,
        state=state,
        send_func=message.reply,
        user_service=user_service
    )


@router.callback_query(F.data.startswith('get_subj|'))
async def get_subject(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        activity_repo: FromDishka[ActivityRepository]
):
    short_stream = cb.data.split('|')[-1]
    data: ChooseStreams = (await state.get_data()).get('chosen_streams')
    stream = data.chosen_streams[short_stream][1]
    await state.clear()
    await state.update_data(current_stream=stream)
    await cb.message.delete()

    await show_subject_details(
        user_id=cb.from_user.id, state=state, stream=stream, activity_repo=activity_repo,
        send_func=lambda *args, **kwargs: bot.send_message(cb.message.chat.id, *args, **kwargs)
    )


@router.callback_query(F.data == 'my_disciplines_add')
async def my_disciplines_add(
        cb: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        service: FromDishka[UserService],
):
    streams: ChooseStreams = await service.get_unselected_user_disciplines(
        user_id=cb.message.chat.id
    )
    await state.update_data(
        chosen_streams=streams,
        confirm={
            'cb': 'my_disciplines_confirm',
            'text': 'Готово'
        },
        other_buttons=[
            [('my_disciplines_back', '↩️Назад')]
        ]
    )
    await cb.message.edit_reply_markup(
        reply_markup=build_start_choose_kb(
            streams.content, streams.chosen_streams,
            0,
            page_cb='my_disciplines_page|',
            confirm='Готово',
            confirm_cb='my_disciplines_confirm',
            other_buttons=[
                [('my_disciplines_back', '↩️Назад')]
            ]
        )
    )


@router.callback_query(F.data == 'my_disciplines_back')
async def my_disciplines_back(
        cb: CallbackQuery,
        state: FSMContext,
        user_service: FromDishka[UserService],
):
    await state.clear()
    await cb.message.delete()
    await show_my_disciplines(
        user_id=cb.from_user.id,
        state=state,
        send_func=lambda *args, **kwargs: cb.message.answer(*args, **kwargs),
        user_service=user_service
    )
