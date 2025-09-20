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
                    text="pollinations.ai", callback_data="generate_image pollinations"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="caila.io", callback_data="generate_image caila"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="neuroimg.art", callback_data="generate_image neuroimg"
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


def get_button_proxies():
    """Возвращает инлайн кнопки выбора получения прокси."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="webshare.io", callback_data="proxies webshare"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_ip():
    """Возвращает инлайн кнопки выбора информации по ip."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Узнать свой api id telegram", callback_data="ip telegram"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Узнать информацию по ip", callback_data="ip ip_info"
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
                InlineKeyboardButton(
                    text="каналы",
                    callback_data="sort channel",
                ),
            ],

        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_model_video_generate_by_caila():
    """Возвращает инлайн кнопки выбора модели для сайта cайта https://caila.io/."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="gpt-image-1", callback_data="gv gpt-image-1"
                ),
            ],
            [
                InlineKeyboardButton(text="dall-e-3", callback_data="gv dall-e-3"),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_recommender_system():
    """Возвращает инлайн кнопки выбора рекомендательной системы."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="кинопоиск", callback_data="recsystem kinopoisk"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_recommender_system_by_kinopoisk():
    """Возвращает инлайн кнопки выбора рекомендательной системы для сайта https://www.kinopoisk.ru/."""

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="По названию фильма", callback_data="kinopoisk_recommender name"
                ),
            ],
        ],
        resize_keyboard=True,
    )
    return inline_kb


def get_button_for_forward_or_back(
    video_search_list: List,
    count: int = 0,
    step: int = 1,
):
    """Возвращает инлайн кнопки для прллистывания назад или вперед."""

    inline_kb = InlineKeyboardBuilder()
    if count == 0:
        if len(video_search_list) == 1:
            pass
        else:
            inline_kb.add(
                InlineKeyboardButton(
                    text="Вперед 👉", callback_data=f"fb forward {count+step}"
                )
            )
    else:
        if len(video_search_list) - count == step:
            inline_kb.add(
                InlineKeyboardButton(
                    text="👈 Назад", callback_data=f"fb back {count-step}"
                )
            )
        elif len(video_search_list) - count >= step:
            inline_kb.add(
                InlineKeyboardButton(
                    text="👈 Назад", callback_data=f"fb back {count-step}"
                )
            )
            inline_kb.add(
                InlineKeyboardButton(
                    text="Вперед 👉", callback_data=f"fb forward {count+step}"
                )
            )
    return inline_kb.as_markup(resize_keyboard=True)
