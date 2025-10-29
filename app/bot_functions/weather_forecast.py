from typing import List, Dict, Optional
import json
import traceback
from pathlib import Path

import folium
import aiohttp

from errors_handlers.main import error_handler_for_the_website
from logging_handler.main import error_logging
from settings.response import ResponseData
from settings.config import settings


async def get_data_weather_forecast_with_openweathermap(
    city: str,
    url_geolocated_openweathermap: str,
    url_future_openweathermap: str,
    url_current_openweathermap: str,
    api_openweathermap: str,
    path_to_weather_translation: Path,
    five_days: bool = False,
) -> ResponseData:
    """Возвращает информацию о текущей погоде или на 5 дней, из данных сайта
       https://openweathermap.org.

    Args:
        city (str): Город для которого нужно узнать информацию
        url_geolocated_openweathermap (str): URL для получения геолокации
        url_future_openweathermap (str): URL для прогноза погоды на 5 дней
        url_current_openweathermap (str): URL для текущего прогноза погоды
        api_openweathermap (str): API для сайта openweathermap
        path_to_weather_translation (str): Путь до файла описаний прогноза погоды
        five_days (bool, optional): Флаг для прогноза погоды.
                                    True - прогнозо погоды на 5 дней
                                    False - прогноз погоды на текущий день

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    try:
        # Формируем url для запроса
        url: str = url_geolocated_openweathermap.format(
            city,
            api_openweathermap,
        )

        async with aiohttp.ClientSession() as session:

            # Получаем данные геолокации для города
            geolocated_response: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url,
            )

            if geolocated_response.error:
                return geolocated_response

            if not geolocated_response.message:
                return ResponseData(
                    error="Такого города не существует",
                    status=geolocated_response.status,
                    method=geolocated_response.method,
                    url=geolocated_response.url,
                )
            data_geolocated: Dict = geolocated_response.message[0]

            lat: float = data_geolocated["lat"]
            lon: float = data_geolocated["lon"]

            # Опредеям прогноз погоды на 5 дней или на текущий день
            list_weather: List = []
            if five_days:
                future_urls: str = url_future_openweathermap.format(
                    lat,
                    lon,
                    api_openweathermap,
                )

                future_response: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=future_urls,
                )
                if future_response.error:
                    return future_response

                for weather in future_response.message["list"]:
                    if weather["dt_txt"].find("12:00:00") != -1:
                        list_weather.append(weather)
            else:
                current_url: str = url_current_openweathermap.format(
                    lat, lon, api_openweathermap
                )
                current_response: ResponseData = await error_handler_for_the_website(
                    url=current_url,
                    session=session,
                )
                if current_response.error:
                    return current_response
                list_weather.append(current_response.message)

        # Достаем словарь перевода описаний погоды

        with open(path_to_weather_translation, "r", encoding="utf-8") as file:
            translate_weather = json.load(file)

        # if five_days:
        array_weather_forecast: List = []

        for weather in list_weather:
            # Провереям есть ли описание погоды в ответе
            try:
                weather_main: str = weather["weather"][0]["main"]
                weather_desc: str = weather["weather"][0]["description"]
                weather_description = translate_weather[weather_main][weather_desc]
            except (KeyError, IndexError, TypeError):
                weather_description = None
            # температура по цельсию
            degree: float = weather["main"]["temp"] - 273.15 
            feels_like: float = (
                weather["main"]["feels_like"] - 273.15
            )  # температура по ощущению
            pressure: int = weather["main"]["pressure"]  # давление гПа
            humidity: int = weather["main"]["humidity"]  # влажность %
            visibility: int = weather.get("visibility", 0)  # видимость m
            wind: float = weather["wind"]["speed"]  # скорость ветра м/c
            clouds: int = weather["clouds"]["all"]
            date: Optional[str] = weather.get("dt_txt", None)

            # Формируем данны для описания
            temperature: str = (
                f"Температура на {date}" if date else "Текущая температура"
            )
            weather_description: str = (
                f"{weather_description[1]} {weather_description[0].title()} {weather_description[1]} \n\n"
                if weather_description
                else ""
            )
            data_weather: str = (
                f"{temperature}\n\n{city}\n\n"
                f"{weather_description}"
                f"🌡 Температура: {round(degree)} °C\n"
                f"🌡 Температура по ощущению: {round(feels_like)} \n"
                f"📊 Давление: {pressure} Гпа\n"
                f"💧 Влажность: {humidity} %\n"
                f"👁️ Видимость: {visibility} м\n"
                f"🌬️ Cкорость ветра: {wind} м/с\n"
                f"☁️ Облачность: {clouds} %"
            )

            # Если текущий прогноз погоды
            if not five_days:
                return ResponseData(
                    message=data_weather,
                    status=200,
                    url=current_response.url,
                    method=current_response.method,
                )
            array_weather_forecast.append(data_weather)

        # Если прогноз погоды на 5 дней
        weather_data: str = "\n\n".join(array_weather_forecast)
        return ResponseData(
            message=weather_data,
            status=200,
            url=future_response.url,
            method=future_response.method,
        )
    except Exception:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method="<unknown>",
                status=0,
                url="<unknown>",
                error_message=f"Unexpected error: {traceback.format_exc()}",
            )
        )
        return ResponseData(
            error="Ошибка на стороне сервера.Идет работа по исправлению...",
            status=0,
            url="<unknown>",
            method="<unknown>",
        )


async def get_air_pollution_city(
    city: str,
    api_openweathermap: str,
    url_geolocated_openweathermap,
    url_air_pollution: str,
    air_pollution: Dict,
    aqi: ResponseData,
) -> Dict:
    """Вовращает данные о уровне загрязнения воздуха, из данных сайта
       https://openweathermap.org

    Args:
        city (str): Название города
        api_openweathermap (str): API для сайта openweathermap
        url_geolocated_openweathermap (_type_): URL для получения геолокации
        url_air_pollution (str): URL для получения данных о загрязнении воздуха
        air_pollution (Dict): Cловарь с компенентами и данными о них
        aqi (Dict): Словарь с номерами и значениями индексов качества воздуха

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    try:
        # Получаем данные геолокации для города
        # API = settings.API_OPENWEATHERMAP
        url_geolocated: str = url_geolocated_openweathermap.format(
            city, api_openweathermap
        )
        async with aiohttp.ClientSession() as session:

            # Получаем геолокацию города
            geolocated_response: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url_geolocated,
            )
            if geolocated_response.error:
                return geolocated_response

            if not geolocated_response.message:
                return ResponseData(
                    error="Такого города не существует",
                    status=geolocated_response.status,
                    url=geolocated_response.url,
                    method=geolocated_response.method,
                )

            data_geolocated: Dict = geolocated_response.message[0]
            lat: float = data_geolocated["lat"]
            lon: float = data_geolocated["lon"]

            url_air_pollution: str = url_air_pollution.format(
                lat, lon, api_openweathermap
            )

            # Делаем запрос на получения данных уровня загрязнения воздуха
            aqi_response: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url_air_pollution,
            )
            if aqi_response.error:
                return aqi_response

        # Получаем словарь с данными по уровню загрязнению воздуха для города
        data_aqii_city = aqi_response.message

        if not data_aqii_city:
            return ResponseData(
                error=f"Нет данных о загрязнении воздух для {city}",
                status=aqi_response.status,
                url=aqi_response.url,
                method=aqi_response.method,
            )

        # Получаем числовое значение индекса загрязнение воздуха
        aqi_city: int = data_aqii_city["list"][0]["main"]["aqi"]

        data: str = f"🌫️ Уровень загрзянения воздуха 🌫️\n\n{city.title()}\n\n"

        air_aqi: str = f"🌡️ Индекс качества воздуха 🌡️\n\n{aqi[aqi_city]}\n\n"

        # Словарь содержащий компоненты и их содержание в воздухе для города
        components_dict: Dict = data_aqii_city["list"][0]["components"]

        list_components: List[str] = [data, air_aqi]

        # Проходимся по компонентам словаря индексов качества воздуха
        for component in air_pollution:

            # Текущее числовое значеие компонента для введенного города
            data = components_dict.get(component, None)
            if not data:
                continue

            # Проходимся по значениям и соответсвующим им числовым выражениям
            for desc, values in air_pollution[component].items():
                if isinstance(values[0], str):
                    break

                # Словарь с данными для компонента
                air_pollution_component: Dict = air_pollution[component]

                # Вычисляем значение компнента для по числовому выражению
                if values[0] <= data < values[1]:
                    data_copmponent: str = (
                        f"{air_pollution_component['emoji']}"  # Эмоджи для компонента
                        f" {component} ({air_pollution_component['translation']}): "  # Название компонента
                        f"{data} - {desc}\n"
                    )
                    list_components.append(data_copmponent)

        air_components: str = "".join(list_components)
        return ResponseData(
            message=air_components,
            status=aqi_response.status,
            url=aqi_response.url,
            method=aqi_response.method,
        )
    except Exception:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method="<unknown>",
                status=0,
                url="<unknown>",
                error_message=f"Unexpected error: {traceback.format_exc()}",
            )
        )
        return ResponseData(
            error="Ошибка на стороне сервера.Идет работа по исправлению...",
            status=0,
            url="<unknown>",
            method="<unknown>",
        )


async def get_weather_map(
    api_openweathermap: str,
    weather_layers: Dict,
    url_weather_map: str,
    path_to_weathermap: Path,
    location_weather: Optional[List] = None,
    filename="weather_layers_map.html",
    zoom=5,
    overlay=True,
    control=True,
    opacity=0.6,
) -> ResponseData:
    """Возвращает карту погоды для из данных сайта https://openweathermap.org

    Args:
        api_openweathermap (str): API для сайта openweathermap
        weather_layers (Dict): Словарь погодных слоёв OpenWeatherMap
        url_weather_map (str): URL для получения карт погоды
        path_to_weathermap: (Path): Путь до папки для сохранения карты погоды
        location_weather (list, optional): Стартовая локация (По умолчанию Москва [55.751244, 37.618423])
        filename (str, optional): Имя файла сохранения (По умолчанию 'weather_layers_map.html')
        zoom (int, optional): Стартовое увеличение (По умолчанию 5)
        overlay (bool, optional): Чтобы слои были поверх карты (По умолчани True)
        control (bool, optional): Чтобы слои можно было влючать/выключать(По умолчанию True)
        opacity (float, optional): Прозрачность от 0(прозрачный) до 1(непрозрачный) (По умолчанию 0.6)

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """

    try:
        # Проверяем доступен ли сайт для получения погоды
        async with aiohttp.ClientSession() as session:
            weather_map: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url_weather_map.format(api_openweathermap),
                data_type="BYTES",
            )

            if weather_map.error:
                return weather_map

        # Если нет стартовой локации добавляем ее
        if not location_weather:
            location_weather: List = settings.LOCATION_WEATHER

        m: folium.Map = folium.Map(
            location=location_weather,
            zoom_start=zoom,
        )

        # Добавляем каждый слой
        for name, layer in weather_layers.items():
            folium.TileLayer(
                tiles=f"https://tile.openweathermap.org/map/{layer}/{{z}}/{{x}}/{{y}}.png?appid={api_openweathermap}",
                attr="OpenWeatherMap",
                name=name,
                overlay=overlay,  # чтобы слой был поверх базовой карты
                control=control,  # чтобы можно было включать/выключать
                opacity=opacity,  # прозрачность (0 — прозрачный, 1 — непрозрачный)
            ).add_to(m)

        # Добавляем управление слоями
        folium.LayerControl().add_to(m)

        # Сохраняем карту погоды
        path_file: Path = path_to_weathermap / filename
        m.save(path_file)

        return ResponseData(
            message=path_file,
            status=200,
            url=weather_map.url,
            method=weather_map.method,
        )

    except Exception:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method="<unknown>",
                status=0,
                url="<unknown>",
                error_message=f"Unexpected error: {traceback.format_exc()}",
            )
        )
        return ResponseData(
            error="Ошибка на стороне сервера.Идет работа по исправлению...",
            status=0,
            url="<unknown>",
            method="<unknown>",
        )
