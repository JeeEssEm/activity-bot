from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def feedback_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text='Назад', callback_data='cancel_leave_feedback')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
