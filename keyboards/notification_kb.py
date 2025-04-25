from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def notification_kb(stream_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text='✔️Зафармил 1 активность',
                callback_data=f'increment_activity_1_{stream_id}'
            ),
            InlineKeyboardButton(
                text='❌Не отвечал',
                callback_data='cancel_increment_activity'
            ),

        ],
        [
            InlineKeyboardButton(
                text='🤯 Зафармил много активностей',
                callback_data=f'increment_activity_n_{stream_id}'
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
