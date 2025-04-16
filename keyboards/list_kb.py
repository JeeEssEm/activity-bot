from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from dtos import StreamDto, StreamDtoDB


def build_start_choose_kb(
        pages: list[list[StreamDto | StreamDtoDB]],
        chosen: dict[str, (bool, StreamDto | StreamDtoDB)],
        page: int,
        page_cb: str,
        confirm: str = None,
        confirm_cb: str = None,
        other_buttons: list[list[tuple[str, str]]] = None
) -> InlineKeyboardMarkup:
    if other_buttons is None:
        other_buttons = []

    total_pages = len(pages)
    arrow_buttons = []
    elements = []
    if total_pages != 0:
        next_page = page_cb + str((page + 1) % total_pages)
        prev_page = page_cb + str(page - 1 if page > 0 else total_pages - 1)
        if total_pages > 1:
            arrow_buttons += [
                InlineKeyboardButton(
                    text='<', callback_data=prev_page,
                ),
                InlineKeyboardButton(
                    text='>', callback_data=next_page,
                ),
            ]
        elements = [
            [InlineKeyboardButton(
                text=(('✅' if chosen[obj.short_stream][0] else '') +
                      obj.truncated()),
                callback_data=obj.get_callback(page)
            )]
            for obj in pages[page]
        ]
    inline_kb = []
    if elements:
        inline_kb.extend(elements)
    if arrow_buttons:
        inline_kb.append(arrow_buttons)
    if other_buttons:
        for row in other_buttons:
            button_row = []
            for cb, text in row:
                button_row.append(InlineKeyboardButton(text=text, callback_data=cb))
            inline_kb.append(button_row)

    inline_kb.append([InlineKeyboardButton(
            text=confirm or 'Готово',
            callback_data=confirm_cb or 'my_disciplines_confirm'
        )])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb)
