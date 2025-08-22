from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
        rezize_keyboard=True,
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
        rezize_keyboard=True,
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
        mrezize_keyboard=True,
    )
    return inline_kb
