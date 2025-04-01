from aiogram import types, Dispatcher, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import FromDishka

from services import UserService
from dtos import ChooseStreams
from keyboards.list_kb import build_list_kb

router = Router()


@router.callback_query(F.data.startswith('my_disciplines_modify|'))
async def modify_list(
        cb: CallbackQuery,
        state: FSMContext
):
    args = cb.data.split('|')
    title = args[-1]
    page = int(args[-2])
    data: ChooseStreams = (await state.get_data()).get('chosen_streams')
    data.chosen_streams[title] = not data.chosen_streams[title]
    await state.update_data(chosen_streams=data)

    await cb.message.edit_reply_markup(reply_markup=build_list_kb(
        pages=data.content,
        chosen=data.chosen_streams,
        page=page,
        page_cb='my_disciplines_page|'
    ))


@router.callback_query(F.data.startswith('my_disciplines_page|'))
async def get_discipline_page(
        cb: CallbackQuery,
        state: FSMContext
):
    data: ChooseStreams = (await state.get_data()).get('chosen_streams')
    page = int(cb.data.split('|')[-1])

    await cb.message.edit_reply_markup(reply_markup=build_list_kb(
        pages=data.content,
        chosen=data.chosen_streams,
        page=page,
        page_cb='my_disciplines_page|'
    ))


@router.callback_query(F.data == '')
async def confirm(
        message: types.Message,
        state: FSMContext,
        service: FromDishka[UserService]
):
    ...

