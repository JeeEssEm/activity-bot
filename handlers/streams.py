from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import FromDishka

from services import UserService
from repositories import StreamRepository
from dtos import ChooseStreams
from keyboards.list_kb import build_start_choose_kb
from constants import LEGEND

router = Router()


@router.callback_query(F.data.startswith('modify_subjs|'))
async def modify_list(
        cb: CallbackQuery,
        state: FSMContext
):
    args = cb.data.split('|')
    title = args[-1]
    page = int(args[-2])
    data: ChooseStreams = (await state.get_data()).get('chosen_streams')
    data.chosen_streams[title][0] = (
        not data.chosen_streams[title][0]
    )
    await state.update_data(chosen_streams=data)

    await cb.message.edit_reply_markup(reply_markup=build_start_choose_kb(
        pages=data.content, chosen=data.chosen_streams, page=page,
        page_cb='my_disciplines_page|'))


@router.callback_query(F.data.startswith('my_disciplines_page|'))
async def get_discipline_page(
        cb: CallbackQuery,
        state: FSMContext
):
    data: ChooseStreams = (await state.get_data()).get('chosen_streams')
    page = int(cb.data.split('|')[-1])

    await cb.message.edit_reply_markup(reply_markup=build_start_choose_kb(
        pages=data.content, chosen=data.chosen_streams, page=page,
        page_cb='my_disciplines_page|'))


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


@router.message(Command('my_disciplines'))
async def get_my_disciplines(
        message: Message,
        state: FSMContext,
        user_service: FromDishka[UserService],
):
    streams = await user_service.get_active_user_disciplines(
        message.from_user.id
    )

    await message.reply(
        f'🗺️Навигатор по типам:{LEGEND}\n'
        f'<b>———</b>\n'
        f'📚<b>Твои дисциплины для отслеживания</b>\n{'\n'.join(links)}'
    )
    # data: ChooseStreams = await user_service.get_user_disciplines(
    #     message.from_user.id, from_db=True)
    # await state.update_data(chosen_streams=data)
    #
    # await message.reply(
    #     f'🗺️Навигатор по типам:{LEGEND}\n'
    #     f'',
    #     reply_markup=build_list_kb(
    #         pages=data.content,
    #         chosen=data.chosen_streams,
    #         page=0,
    #         page_cb='my_disciplines_page|'
    #     )
    # )
