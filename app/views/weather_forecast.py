import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import (
    get_button_is_weathre_forecast,
    get_button_is_weathre_maps,
)
from keyboards.reply_kb import get_start_button_bot, get_cancel_button
from functions import (
    get_data_current_weather_forecast_with_openweathermap,
    get_and_save_image,
    get_air_pollution_city,
)
from extension import bot
from config import settings

router = Router(name=__name__)


@router.message(F.text == "Прогноз Погоды")
async def get_weather_forecast(message: Message):
    """Возвращает кнопки для выбора вариантов прогноза погоды."""

    await bot.send_message(
        text="Прогноз Погоды",
        chat_id=message.chat.id,
        reply_markup=ReplyKeyboardRemove(),
    )

    await message.answer(
        text="Выберите варианты прогноза погоды",
        reply_markup=get_button_is_weathre_forecast(),
    )


# логика для определения текущего прогнозоа погоды
class CurrentWeather(StatesGroup):
    """FSM для текущего прогноза погоды"""

    current_weather = State()


@router.callback_query(F.data == "current_weather")
async def start_current_weather(call: CallbackQuery, state: FSMContext):
    """Работа с FSM CurrentWeather.Просит пользователя ввести название города."""

    await call.message.answer(
        "Введите название города для которого хотите узнать прогноз погоды",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(CurrentWeather.current_weather)


@router.message(CurrentWeather.current_weather, F.text == "Отмена")
async def cancel_handler_current_weather(message: Message, state: FSMContext):
    """Отменяет действия работы FSM CurrentWeather."""

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(text="Прогнозо погоды на текущий день отменен")
    await bot.send_message(
        text="Главное меню бота",
        chat_id=message.chat.id,
        reply_markup=get_start_button_bot(),
    )


@router.message(CurrentWeather.current_weather, F.text)
async def finish_current_weaher(message: Message, state: FSMContext):
    """Работа с FSM CurrentWeather.Возвращает пользователю прогноз погоды для города."""
    city = message.text
    data, mess = get_data_current_weather_forecast_with_openweathermap(
        city=city,
    )

    if not data:
        await message.answer(
            text="Такого города не существует\n\n"
            "Введите снова название города для которого хотите узнать прогноз погоды",
            reply_markup=get_cancel_button(),
        )
    else:
        await message.answer(
            text=data,
        )
        await bot.send_message(
            text="Главное меню бота",
            chat_id=message.chat.id,
            reply_markup=get_start_button_bot(),
        )
        await state.clear()


# логика для определения прогноза на 5 дней
class FeautureWeather(StatesGroup):
    """FSM для прогноза погоды на 5 дней"""

    feautre_weather = State()


@router.callback_query(F.data == "future_weaher")
async def start_feature_weather(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FeautureWeather.Просит пользователя ввести название города."""

    await call.message.answer(
        "Введите название города для которого хотите узнать прогноз погоды",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(FeautureWeather.feautre_weather)


@router.message(FeautureWeather.feautre_weather, F.text == "Отмена")
async def cancel_feature_weather(message: Message, state: FSMContext):
    """Работа с FSM FeautureWeather.Отменяет все действия по прогнозу погоды на 5 дней."""

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(text="Прогнозо погоды на 5 дней отменен")
    await bot.send_message(
        text="Главное меню бота",
        chat_id=message.chat.id,
        reply_markup=get_start_button_bot(),
    )


@router.message(FeautureWeather.feautre_weather, F.text)
async def finish_feature_weather(message: Message, state: FSMContext):
    """Работа с FSM FeautureWeather.Выводит информацию о погоде на 5 дней указаного города."""
    data, mess = get_data_current_weather_forecast_with_openweathermap(
        city=message.text, five_days=True
    )

    if data:
        await state.clear()
        await message.answer(data)
        await message.answer(
            text="Главное меню бота",
            reply_markup=get_start_button_bot(),
        )
    else:
        await message.answer(
            "Такого города не существует\n\n"
            "Введите снова название города для которого хотите узнать прогноз погоды"
        )


# Работа с картами погоды
@router.callback_query(F.data == "weather_maps")
async def handler_weather_maps(call: CallbackQuery):
    """Возвращает пользователю инлайн кнопки карт погоды"""

    await call.message.answer(
        text="Карты погоды",
        reply_markup=get_button_is_weathre_maps(),
    )


@router.callback_query(F.data.startswith("weather "))
async def get_worlwipe_weather_maps(call: CallbackQuery):
    """Возвращает карту погоды."""
    _, weather = call.data.split(" ")

    url = settings.URL_WEATHER_MAPS.format(weather, settings.API_OPENWEATHERMAP)

    # Получает карту погоды
    path = get_and_save_image(url=url, filename="weather.png")

    await bot.send_photo(
        chat_id=call.message.chat.id,
        caption="Карта погоды",
        photo=FSInputFile(path=path),
        reply_markup=get_button_is_weathre_forecast(),
    )

    # Удаляет карты погоду
    os.remove(path)


# логика для определения уровня загрязнения воздуха
class AirPollution(StatesGroup):
    """FSM уровня загрязнения воздуха."""

    polution = State()


@router.callback_query(F.data == "air_pollution")
async def air_pollution(call: CallbackQuery, state: FSMContext):
    """Работа с FSM AirPollution. Просит пользователя ввести названиае города."""

    await call.message.answer(
        text="Введите нзавание города для которого хотите узнать уровень загрязнения воздуха",
        reply_markup=get_cancel_button(),
    )

    await state.set_state(AirPollution.polution)


@router.message(AirPollution.polution, F.text == "Отмена")
async def cancel_air_polution_handler(message: Message, state: FSMContext):
    """Работа с AirPollution.Отменяет выдачу уровня загрзнения воздуха по городу."""

    current_state = state.get_state()
    if current_state is None:
        return

    await message.answer(
        text="Уровень загрязнения воздуха отменен",
        reply_markup=ReplyKeyboardRemove(),
    )
    await get_weather_forecast(message=message)
    await state.clear()


@router.message(AirPollution.polution, F.text)
async def get_air_polution(message: Message, state: FSMContext):
    """Работа с FSM AirPollution. Возвращает пользователю данные по уровню загрязнения воздуха."""
    data, mess = get_air_pollution_city(city=message.text)

    if data:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Данные по уровню загрязнения воздуха",
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(text=data)
        await get_weather_forecast(message=message)
        await state.clear()
    else:
        await message.answer(
            text=f"{mess['error']}\n\n"
            "Введите снова нзавание города для которого хотите узнать уровень загрязнения воздуха"
        )
