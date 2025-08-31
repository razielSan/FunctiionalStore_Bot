from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_button_is_weathre_forecast():
    """Возвращает инлайн кнопки для выбора варинтов прогноза погоды."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Текущий прогноз погоды", callback_data="current_weather"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Прогноз погоды на 5 дней", callback_data="future_weaher"
                ),
            ],
            [
                InlineKeyboardButton(text="Карты погоды", callback_data="weather_maps"),
            ],
            [
                InlineKeyboardButton(
                    text="Уровень загрязнения воздуха", callback_data="air_pollution"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_is_weathre_maps():
    """Возвращает инлайн кнопки для карт погоды."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="☁️ Облака ☁️", callback_data="weather clouds_new"
                ),
                InlineKeyboardButton(
                    text="☔ Осадки ☔", callback_data="weather precipitation_new"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Давление на уровне моря 📊",
                    callback_data="weather pressure_new",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌬️ Скорость ветра 🌬️", callback_data="weather wind_new"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌡 Температура 🌡", callback_data="weather temp_new"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_generate_image():
    """Возвращает инлайн кнопки выбора генераторов изображений."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="pollinations.ai", callback_data="pollinations"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_image_description():
    """Возвращает инлайн кнопки выбора генераторов описаний изображений."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="imagga.com", callback_data="immaga"),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_find_video():
    """Возвращает инлайн кнопки выбора вариантов поиска видео."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="youtube.com", callback_data="FindVideo youtube"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_choice_sorted_youtube_video():
    """Возвращает инлайн кнопки выбора вариантов варианта сортировки youtube видео"""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="по дате создания",
                    callback_data="sort date",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="по релевантности",
                    callback_data="sort relevance",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="по рейтингу",
                    callback_data="sort rating",
                ),
                InlineKeyboardButton(
                    text="по названию",
                    callback_data="sort title",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="по просмотрам",
                    callback_data="sort viewCount",
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb
