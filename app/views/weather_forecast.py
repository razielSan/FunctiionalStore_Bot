import os
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from keyboards.inline_kb import (
    get_button_is_weathre_forecast,
)
from keyboards.reply_kb import get_start_button_bot, get_cancel_button

from bot_functions.weather_forecast import (
    get_data_weather_forecast_with_openweathermap,
    get_weather_map,
    get_air_pollution_city,
)
from extension import bot
from settings.config import settings
from settings.response import ResponseData


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Прогноз Погоды")
async def get_weather_forecast(message: Message):
    """Возвращает кнопки для выбора вариантов прогноза погоды."""

    await bot.send_message(
        text="Прогноз Погоды",
        chat_id=message.chat.id,
        reply_markup=get_start_button_bot(),
    )

    await message.answer(
        text="Выберите варианты прогноза погоды",
        reply_markup=get_button_is_weathre_forecast(),
    )


# логика для определения текущего прогнозоа погоды
class CurrentWeather(StatesGroup):
    """FSM для текущего прогноза погоды"""

    spam: State = State()
    current_weather: State = State()


@router.callback_query(F.data == "current_weather")
async def start_current_weather(call: CallbackQuery, state: FSMContext):
    """Работа с FSM CurrentWeather.Для текущего прогноза погоды.
    Просит пользователя ввести название города.
    """

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        "Введите название города для которого хотите узнать прогноз погоды",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(CurrentWeather.current_weather)


@router.message(CurrentWeather.current_weather, F.text == "Отмена")
async def cancel_current_weather_handler(message: Message, state: FSMContext):
    """Работа с FSM CurrentWeather.Отменяет все действия."""

    await state.clear()
    await message.answer(text="Текущий прогноз погоды отменен....")
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(CurrentWeather.spam, F.text)
async def get_message_for_current_weather(message: Message, state: FSMContext):
    """Работа с FSM CurrentWeather.Отправляет пользователю сообщение если он
    ввел текст обработке запроса на получение данных о текущей погоде.
    """

    await message.reply(text="Идет обработка запроса, пожалуйста подождите...")


@router.message(CurrentWeather.current_weather, F.text)
async def finish_current_weaher(message: Message, state: FSMContext):
    """Работа с FSM CurrentWeather.Возвращает пользователю текущий прогноз погоды для города."""

    # Встаем в состояние spam для отловки сообщений при обработке запроса
    await state.set_state(CurrentWeather.spam)

    await bot.send_message(
        chat_id=message.chat.id,
        text="Идет обработка запроса....",
        reply_markup=ReplyKeyboardRemove(),
    )
    await asyncio.sleep(1)

    # Получаем данные текущего прогноза погоды
    weather_data: ResponseData = await get_data_weather_forecast_with_openweathermap(
        city=message.text,
        url_current_openweathermap=settings.URL_CURRENT_OPENWEATHERMAP,
        url_future_openweathermap=settings.URL_FEATURE_OPENWEATHERMAP,
        url_geolocated_openweathermap=settings.ULR_GEOLOCATED_OPENWEATHERMAP,
        api_openweathermap=settings.API_OPENWEATHERMAP,
        path_to_weather_translation=settings.PATH_TO_WEATHER_TRANSLATION,
        five_days=False,
    )

    if weather_data.error:
        await state.set_state(CurrentWeather.current_weather)
        await message.answer(
            text=f"{weather_data.error}\n\nВведите, снова, название города"
            " для которого хотите узнать прогноз погоды",
            reply_markup=get_cancel_button(),
        )

    else:
        await state.clear()
        await message.answer(
            text=weather_data.message,
        )
        await bot.send_message(
            text="Главное меню бота",
            chat_id=message.chat.id,
            reply_markup=get_start_button_bot(),
        )


# логика для определения прогноза на 5 дней
class FutureWeather(StatesGroup):
    """FSM для прогноза погоды на 5 дней"""

    spam: State = State()
    future_weather: State = State()


@router.callback_query(F.data == "future_weaher")
async def start_feature_weather(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FutureWeather.Для прогноза погоды на 5 дней.
    Просит пользователя ввести название города.
    """
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "Введите название города для которого хотите узнать прогноз погоды",
        reply_markup=get_cancel_button(),
    )

    await state.set_state(FutureWeather.future_weather)


@router.message(FutureWeather.future_weather, F.text == "Отмена")
async def cancel_future_weather_handler(message: Message, state: FSMContext):
    """Работа с FSM FutureWeather.Отменяет все действия."""

    await state.clear()
    await message.answer(text="Прогноз погоды на 5 дней отменен....")
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(FutureWeather.spam, F.text)
async def get_spam_message(message: Message, state: FSMContext):
    """Работа с FSM FutureWeather.Отправляет пользователю сообщение при
    обработке информации.
    """
    await message.reply(text="Идет обработка запроса, пожалуйста подождите...")


@router.message(FutureWeather.future_weather, F.text)
async def finish_feature_weather(message: Message, state: FSMContext):
    """Работа с FSM FutureWeather.Выводит информацию о погоде на 5 дней указаного города."""

    # Встаем в состояние FutureWeather.spam если пользователь напишет сообщение пока идет
    # обработка информации
    await state.set_state(FutureWeather.spam)

    await bot.send_message(
        chat_id=message.chat.id,
        text="Идет обработка запроса....",
        reply_markup=ReplyKeyboardRemove(),
    )
    await asyncio.sleep(1)
    weather_data: ResponseData = await get_data_weather_forecast_with_openweathermap(
        city=message.text,
        url_current_openweathermap=settings.URL_CURRENT_OPENWEATHERMAP,
        url_future_openweathermap=settings.URL_FEATURE_OPENWEATHERMAP,
        url_geolocated_openweathermap=settings.ULR_GEOLOCATED_OPENWEATHERMAP,
        api_openweathermap=settings.API_OPENWEATHERMAP,
        path_to_weather_translation=settings.PATH_TO_WEATHER_TRANSLATION,
        five_days=True,
    )

    if weather_data.message:
        await state.clear()
        await message.answer(
            text=weather_data.message,
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text="Главное меню бота",
            reply_markup=get_start_button_bot(),
        )
    else:
        await state.set_state(FutureWeather.future_weather)
        await message.answer(
            text=f"{weather_data.error}\n\nВведите, снова, название города для "
            "которого хотите узнать прогноз погоды",
            reply_markup=get_cancel_button(),
        )


# Работа с картами погоды
@router.callback_query(F.data == "weather_maps")
async def handler_weather_maps(call: CallbackQuery):
    """Возвращает карту погоды."""

    await call.message.edit_reply_markup(reply_markup=None)

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="Идет обработка запроса....",
        reply_markup=ReplyKeyboardRemove(),
    )
    await asyncio.sleep(1)

    # Получаем карту погоды
    data_weather_map: ResponseData = await get_weather_map(
        api_openweathermap=settings.API_OPENWEATHERMAP,
        weather_layers=settings.WEATHER_LAYERS,
        filename="weather_map.html",
        url_weather_map=settings.URL_WEATHER_MAPS,
        path_to_weathermap=settings.PATH_TO_WEATHER_MAP,
        location_weather=settings.LOCATION_WEATHER,
    )

    if data_weather_map.message:
        await bot.send_document(
            chat_id=call.message.chat.id,
            document=FSInputFile(
                path=data_weather_map.message,
            ),
        )
        await call.message.answer(
            text="Главное меню бота",
            reply_markup=get_start_button_bot(),
        )
        os.remove(data_weather_map.message)
    else:
        await bot.send_message(
            chat_id=call.message.chat.id, text=data_weather_map.error
        )
        await bot.send_message(
            chat_id=call.message.chat.id,
            text="Варианты выбора",
            reply_markup=get_start_button_bot(),
        )


# логика для определения уровня загрязнения воздуха
class AirPollution(StatesGroup):
    """FSM уровня загрязнения воздуха."""

    spam: State = State()
    polution: State = State()


@router.callback_query(F.data == "air_pollution")
async def air_pollution(call: CallbackQuery, state: FSMContext):
    """Работа с FSM AirPollution. Просит пользователя ввести названиае города."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text="Введите нзавание города для которого хотите узнать уровень загрязнения воздуха",
        reply_markup=get_cancel_button(),
    )

    await state.set_state(AirPollution.polution)


@router.message(AirPollution.polution, F.text == "Отмена")
async def cancel_air_pollution_handler(message: Message, state: FSMContext):
    """Работа с FSM AirPollution.Отменяет все действия."""

    await state.clear()
    await message.answer(text="Уровень загрязнения воздуха отменен....")
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(AirPollution.spam, F.text)
async def get_message_for_air_pollution(message: Message, state: FSMContext):
    """Работа с FSM CurrentWeather.Отправляет пользователю сообщение если он
    ввел текст при обработке запроса на получение данных о уровне загрязнения воздуха.
    """

    await message.reply(text="Идет обработка запроса, пожалуйста подождите...")


@router.message(AirPollution.polution, F.text)
async def get_air_polution(message: Message, state: FSMContext):
    """Работа с FSM AirPollution. Возвращает пользователю данные по уровню загрязнения воздуха."""

    # Встаем в состояние spam для отловки сообщений при обработке запроса
    await state.set_state(AirPollution.spam)

    await bot.send_message(
        chat_id=message.chat.id,
        text="Идет обработка запроса....",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Получаем данные по загрязнению воздуха
    air_pollution_data: ResponseData = await get_air_pollution_city(
        city=message.text,
        api_openweathermap=settings.API_OPENWEATHERMAP,
        url_air_pollution=settings.URL_AIR_POLLUTION,
        url_geolocated_openweathermap=settings.ULR_GEOLOCATED_OPENWEATHERMAP,
        air_pollution=settings.AIR_POLLUTION,
        aqi=settings.AQI,
    )

    if air_pollution_data.message:
        await state.clear()

        await message.answer(
            text=air_pollution_data.message,
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(
            text="Главное меню бота",
            reply_markup=get_start_button_bot(),
        )
    else:
        await state.set_state(AirPollution.polution)
        await message.answer(
            text=f"{air_pollution_data.error}\n\nВведите,"
            " снова, нзавание города для которого хотите узнать уровень"
            " загрязнения воздуха",
            reply_markup=get_cancel_button(),
        )
