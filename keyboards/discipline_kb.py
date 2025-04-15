from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from dtos import StreamDtoDB


def build_discipline_kb(
        stream_id: int
) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text='🔄Изменить количество активностей',
            callback_data=f'set_activity_{stream_id}'
        )],
        [InlineKeyboardButton(
            text='🚶‍♂️🚶‍♂️🚶‍♂️Очередь за активностью',
            callback_data=f'queue_activity_{stream_id}'
        )],
        [InlineKeyboardButton(
            text='❌Перестать отслеживать',
            callback_data=f'stop_tracking_{stream_id}'
        )],
        # [InlineKeyboardButton('Уведомления', callback_data=f'')], # TODO: in future :)
        [InlineKeyboardButton(
            text='↩️Назад',
            callback_data=f'my_disciplines'
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def ensure_delete_kb(
        stream: StreamDtoDB
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text='✔️Да', callback_data=f'confirm_stop_tracking_{stream.id}'),
            InlineKeyboardButton(text='❌Нет', callback_data=f'get_subj|{stream.short_stream}'),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
