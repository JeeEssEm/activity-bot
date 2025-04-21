from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from dtos import StreamDtoDB


def build_discipline_kb(
        stream_id: int,
        notify: bool
) -> InlineKeyboardMarkup:
    notification_text = '🔕Заглушить'
    if not notify:
        notification_text = '🔔Включить уведомления'

    buttons = [
        [InlineKeyboardButton(
            text='🔄Изменить количество активностей',
            callback_data=f'set_activity_{stream_id}'
        )],
        [InlineKeyboardButton(
            text='🚶‍♂️🚶‍♂️🚶‍♂️Очередь за активностью',
            callback_data=f'queue_activity'
        )],
        [InlineKeyboardButton(
            text='❌Перестать отслеживать',
            callback_data=f'stop_tracking_{stream_id}'
        )],
        [InlineKeyboardButton(
            text=notification_text,
            callback_data=f'change_notification_status_{int(not notify)}'
        )],
        [InlineKeyboardButton(
            text='↩️Назад',
            callback_data=f'my_disciplines_back'
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def ensure_delete_kb(
        yes_cb: str,
        no_cb: str
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text='✔️Да', callback_data=yes_cb),
            InlineKeyboardButton(text='❌Нет', callback_data=no_cb),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def change_activities() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='↩️Назад', callback_data='cancel_set_activity')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
