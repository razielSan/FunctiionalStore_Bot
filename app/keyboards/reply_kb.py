from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_start_button_bot():
    """Возвращает кнопки для главного меню бота."""

    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Прогноз Погоды"),
            ],
            [
                KeyboardButton(text="Поиск Изображений"),
                KeyboardButton(text="Поиск Видео"),
            ],
            [
                KeyboardButton(text="Генерация Изображений"),
                KeyboardButton(text="Описание Изображений"),
            ],
        ],
        resize_keyboard=True,
    )

    return reply_kb


def get_cancel_button():
    """Возвращает кнопку отмены."""
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
    )

    return reply_kb
