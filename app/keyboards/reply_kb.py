from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_start_button_bot() -> ReplyKeyboardMarkup:
    """Возвращает кнопки для главного меню бота."""

    reply_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
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
            ],
            [
                KeyboardButton(text="Информация по ip"),
                KeyboardButton(text="Получить список прокси"),
            ],
            [
                KeyboardButton(text="Рекомендательная система"),
                KeyboardButton(text="Генерация паролей")
            ]
        ],
        resize_keyboard=True,
    )

    return reply_kb


def get_cancel_button() -> ReplyKeyboardMarkup:
    """Возвращает кнопку отмены."""
    reply_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
    )

    return reply_kb
