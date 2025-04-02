from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from dtos import StreamDto


def build_list_kb(
        pages: list[list[StreamDto]],
        chosen: dict[str, (bool, StreamDto)],
        page: int,
        page_cb: str
) -> InlineKeyboardMarkup:
    total_pages = len(pages)
    next_page = page_cb + str((page + 1) % total_pages)
    prev_page = page_cb + str(max(0, page - 1))

    arrow_buttons = []
    if page != 0:
        arrow_buttons += [
            InlineKeyboardButton(text='<<', callback_data=page_cb + '0'),
            InlineKeyboardButton(text='<', callback_data=prev_page)
        ]
    if page != total_pages - 1:
        arrow_buttons += [
            InlineKeyboardButton(text='>', callback_data=next_page),
            InlineKeyboardButton(
                text='>>',
                callback_data=page_cb + str(total_pages - 1)
            )
        ]

    inline_kb = [
        *[
            [InlineKeyboardButton(
                text=(('✅' if chosen[obj.short_stream][0] else '') +
                      obj.truncated()),
                callback_data=obj.get_callback(page)
            )]
            for obj in pages[page]
        ],
        arrow_buttons,
        [InlineKeyboardButton(
            text='Готово', callback_data='my_disciplines_confirm'
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)
