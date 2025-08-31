from typing import Dict
import os
import sys
import json
from pathlib import Path

import requests
from icrawler.builtin import BingImageCrawler
from googleapiclient.discovery import build

from config import settings


def get_data_current_weather_forecast_with_openweathermap(
    city: str,
    five_days: bool = False,
):
    """
    Возвращает информацию о текущей погоде из данных сайта https://openweathermap.org и состояние о выполнение запроса.

    Args:
        city (str): Город для которого нужно узнать погоду
    """
    try:
        url = settings.ULR_GEOLOCATED_OPENWEATHERMAP.format(
            city, settings.API_OPENWEATHERMAP
        )

        # Получаем данные геолокации для города
        geolocated_response = requests.get(url).json()
        data_geolocated = geolocated_response[0]
        lat = data_geolocated["lat"]
        lon = data_geolocated["lon"]

        current_url = ""
        if five_days:
            feature_urls = settings.URL_FEATURE_OPENWEATHERMAP.format(
                lat, lon, settings.API_OPENWEATHERMAP
            )
            response = requests.get(feature_urls).json()
            list_weather = []
            for weather in response["list"]:
                if weather["dt_txt"].find("12:00:00") != -1:
                    list_weather.append(weather)
        else:
            current_url = settings.URL_CURRENT_OPENWEATHERMAP.format(
                lat, lon, settings.API_OPENWEATHERMAP
            )
            response = requests.get(current_url).json()

        # Достаем словарь перевода описаний погоды
        weather_translation = os.path.join(
            sys.path[0], settings.PATH_TO_WEATHER_TRANSLATION
        )
        with open(weather_translation, "r", encoding="utf-8") as file:
            translate_weather = json.load(file)

        if five_days:
            array_weather_forecast = []
            for weather in list_weather:
                weather_main = weather["weather"][0]["main"]
                weather_desc = weather["weather"][0]["description"]
                weather_description = translate_weather[weather_main][weather_desc]
                degree = weather["main"]["temp"] - 273.15  # температура по цельсию
                feels_like = (
                    weather["main"]["feels_like"] - 273.15
                )  # температура по ощущению
                pressure = weather["main"]["pressure"]  # давление гПа
                humidity = weather["main"]["humidity"]  # влажность %
                visibility = weather["visibility"]  # видимость m
                wind = weather["wind"]["speed"]  # скорость ветра м/c
                clouds = weather["clouds"]["all"]
                date = weather["dt_txt"]

                data_weather = (
                    f"Темпаратура на {date}\n\n{city}\n\n{weather_description[1]} {weather_description[0].title()} {weather_description[1]} \n\n"
                    f"🌡 Температура: {int(degree)} градусов по цельсию 🌡\n"
                    f"🌡 Температура по ощущению: {int(feels_like)} градусов по цельсию 🌡\n"
                    f"📊 Давление: {pressure} Гпа 📊\n"
                    f"💧 Влажность: {humidity} % 💧\n"
                    f"👁️ Видимость: {visibility} м 👁️\n"
                    f"🌬️ Cкорость ветра: {wind} м/с 🌬️\n"
                    f"☁️ Облачность: {clouds} % ☁️"
                )
                array_weather_forecast.append(data_weather)
            weather_data = "\n\n".join(array_weather_forecast)
            return weather_data, {"error": None}
        else:
            weather_main = response["weather"][0]["main"]
            weather_desc = response["weather"][0]["description"]
            weather_description = translate_weather[weather_main][weather_desc]
            degree = response["main"]["temp"] - 273.15  # температура по цельсию
            feels_like = (
                response["main"]["feels_like"] - 273.15
            )  # температура по ощущению
            pressure = response["main"]["pressure"]  # давление гПа
            humidity = response["main"]["humidity"]  # влажность %
            visibility = response["visibility"]  # видимость m
            wind = response["wind"]["speed"]  # скорость ветра м/c
            clouds = response["clouds"]["all"]

            data_weather = (
                f"Текущая температура\n\n{city}\n\n{weather_description[1]} {weather_description[0].title()} {weather_description[1]} \n\n"
                f"🌡 Температура: {int(degree)} градусов по цельсию 🌡\n"
                f"🌡 Температура по ощущению: {int(feels_like)} градусов по цельсию 🌡\n"
                f"📊 Давление: {pressure} Гпа 📊\n"
                f"💧 Влажность: {humidity} % 💧\n"
                f"👁️ Видимость: {visibility} м 👁️\n"
                f"🌬️ Cкорость ветра: {wind} м/с 🌬️\n"
                f"☁️ Облачность: {clouds} % ☁️\n"
            )

            return data_weather, {"error": None}

    except Exception as err:
        print(err)
        return None, {"error": "Неверный формат данных"}


def find_image_with_goole_and_save_image(
    name: str,
    count: int,
    filters: Dict,
    path: str,
):
    """Ищет картинки в google.com и сохраняет их.
    Возвращает кортеж формата

    (True, {'err': None}) - Картинки успешно найдены и скачены
    (None, {'err': <Сообщение об ошибки>}) - Картинки не найдены

    Args:
        name (str): Имя картинки
        count (int): Количество изображений для скачивания
        filters (Dict): Фильтры для изображения
        path (str): Путь куда будут залиты изображения
    """
    try:
        google = BingImageCrawler(storage={"root_dir": path})
        google.crawl(keyword=name, max_num=count, filters=filters)
        return True, {"err": None}
    except Exception as err:
        print(err)
        return False, {"err": "Произошла ошибка скачивания"}


def delete_images_and_archive(path_archive: str, count_images: int):
    """Удаляет архив и изображения по указынным путям.
    Имена картинок берутся от 000001 до 999999 в разрешении jpg

    Args:
        path_archive (str): Путь до архива
        count_images (int): Количество картинок которые нужно удалить.
    """

    if os.path.exists(path=path_archive):
        os.remove(path_archive)
    for number in range(1, count_images + 1):
        path = os.path.join(sys.path[0], f"{number:06}.jpg")
        if os.path.exists(path):
            os.remove(path)


def get_and_save_image(url: str, filename: str):
    """Возвращает скачанную с url картинку
    Args:
        url (str): URL для скачивания картинки
        filename (str, optional): Имя файла
    """
    try:
        response = requests.get(url)

        with open(filename, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        path = os.path.join(sys.path[0], filename)
        return path
    except Exception as err:
        print(err)
        return False


def get_air_pollution_city(city: str):
    """Возвращает данные о уровне загрязнения воздуха в городе
    (<Данные_о_уровне_загрязнения_воздуха>, {"error": None}) - Если данные успешно собраны
    (None, {"error": <Сообщение_об_ошибке>}) - Если данные не удалось собрать

    Args:
        city (str): Название города
    """
    try:
        # Получаем данные геолокации для города
        API = settings.API_OPENWEATHERMAP
        url_geolocated = settings.ULR_GEOLOCATED_OPENWEATHERMAP.format(city, API)
        geolocated_response = requests.get(url_geolocated).json()
        data_geolocated = geolocated_response[0]
        lat = data_geolocated["lat"]
        lon = data_geolocated["lon"]

        url = settings.URL_AIR_POLLUTION.format(lat, lon, API)

        response = requests.get(url).json()

        aqi = response["list"][0]["main"]["aqi"]

        data = f"🌫️ Уровень загрзянения воздуха 🌫️\n\n{city.title()}\n\n"

        air_aqi = f"🌡️ Индекс качества воздуха 🌡️\n\n{aqi} - {settings.AQI[aqi]}\n\n"

        components_dict = response["list"][0]["components"]

        list_components = [data, air_aqi]
        for component in settings.AIR_POLLUTION:
            data = components_dict[component]
            for desc, values in settings.AIR_POLLUTION[component].items():
                if isinstance(values[0], str):
                    break
                air_pollution = settings.AIR_POLLUTION[component]
                if data >= values[0] and data < values[1]:
                    data_copmponent = f"{air_pollution['emoji']} {component} ({air_pollution['translation']}): {data} - {desc} {air_pollution['emoji']}\n"
                    list_components.append(data_copmponent)

        air_components = "".join(list_components)
        return air_components, {"error": None}
    except Exception as err:
        print(err)
        return None, {"error": "Города с таким названием не существует"}


def get_image_description_by_immaga(
    language="en",
    limit=-1,
):
    """Возвращает описание картинки для сайта https://imagga.com/.

    Args:
        language (str, optional): Язык описания изображений.По умолчанию английский
        limit (int, optional): Количество описаний.По умолчанию максимальное

    Returns:
        _type_: Кортеж содержащий описание картинки и сообщение об ошибке, если имеется
        (<image_description>, {"err": None}) - Если запрос прошел успешно
        (None, {"err": <message_error>}) - Если произошла ошибка
    """
    try:
        path_image = Path(__file__).parent

        full_path = os.path.join(path_image, "immaga.jpg")

        response = requests.post(
            settings.image_description.immaga.UPLOADEN_ENDPOINT,
            headers={
                "Authorization": f"Basic {settings.image_description.immaga.AUTHORIZATION}",
            },
            files={"image": open(full_path, "rb")},
        )

        uload_id = response.json()["result"]["upload_id"]

        response_imaage_description = requests.get(
            f"{settings.image_description.immaga.URL_TAGS}image_upload_id="
            f"{uload_id}&language={language}&limit={limit}",
            headers={
                "Authorization": f"Basic {settings.image_description.immaga.AUTHORIZATION}",
            },
        ).json()

        array_image_description = [
            "Список возможных вариантов изображения на картинке:\n"
        ]

        for data in response_imaage_description["result"]["tags"]:
            array_image_description.append(
                f"{data['tag']['ru'].title()} ({data['confidence']:.3f}%) "
            )

        result = "\n".join(array_image_description)
        return result, {"err": None}

    except Exception as err:
        return None, {"err": err}


def get_description_video_by_youtube(
    name_video: str,
    sort: str,
):
    service = build(
        "youtube", "v3", developerKey=settings.find_video.youtube.YoutubeApiKey
    )

    response = (
        service.search()
        .list(
            q=name_video,
            part="snippet",
            relevanceLanguage="ru",
            type="video",
            maxResults=50,
            order=sort,
        )
        .execute()
    )

    array_video_description = []
    order = 0
    for result in response["items"]:
        order += 1
        video_url = None
        channel_url = None
        try:
            video_id = result["id"]["videoId"]
            video_url = settings.find_video.youtube.VIDEO_URL.format(video_id)
        except Exception:
            channel_id = result["id"]["channelId"]
            channel_url = settings.find_video.youtube.CHANNEL_URL.format(channel_id)

        title = result["snippet"]["title"].replace("&quot;", " ")
        description = result["snippet"]["description"].replace("&quot;", " ")

        if video_url:
            array_video_description.append(
                f"{order}. {title}\n\n{description}\n\nСсслыка на видео\n{video_url}\n"
            )
        else:
            array_video_description.append(
                f"{order}. {title}\n\n{description}\n\nСсслыка на канал\n{channel_url}\n"
            )

    return array_video_description
