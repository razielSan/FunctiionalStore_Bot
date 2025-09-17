from typing import Dict, Optional, List
import os
import sys
import json
from pathlib import Path
import base64
import random

import requests
from aiogram.utils.markdown import hbold
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


def get_and_save_image(
    url: str,
    filename: str,
    gpt_image_1=None,
):
    """Возвращает скачанную с url картинку
    Args:
        url (str): URL для скачивания картинки
        filename (str, optional): Имя файла
    """
    try:
        if gpt_image_1:
            image_file = base64.b64decode(url)
            with open(filename, "wb") as image:
                image.write(image_file)
        else:
            response = requests.get(url)

            with open(filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

        path = os.path.join(sys.path[0], filename)
        return path
    except Exception as err:
        print(err)
        return False


def get_url_video_generate_by_caila(
    url: str,
    api_key: str,
    model: str,
    promtp: str,
    size: str = "1024x1024",
    quality_gpt_image_1: str = "low",
    quality_dall_e_3: str = "standard",
):
    """Возвращает b64_json или url для скачивания изображения

    Работа с сайтом https://caila.io/

    Args:
        url (str): URL генерации изображения
        api_key (str): API Key для доступа
        model (str): модель генерации изображения
        promtp (str): описание изображения
        size (str, optional): размер изображения
        quality_gpt_image_1 (str, optional): качество для модели gpt-image-1
        quality_dall_e_3 (str, optional): качество для модели dall-e-3

    Returns:
        _type_: Возвращае b64_json или url для скачивания
    """
    quality = "low"
    if model == "gpt-image-1":
        quality = quality_gpt_image_1
    elif model == "dall-e-3":
        quality = quality_dall_e_3

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    json_data = json.dumps(
        {
            "model": f"just-ai/openai-proxy/{model}",
            "prompt": promtp,
            "quality": quality,
            "size": size,
        },
    )
    response = requests.post(url, headers=HEADERS, data=json_data)

    if response.status_code == 400:
        return response.status_code

    if model == "dall-e-3":
        return response.json()["data"][0]["url"]
    elif model == "gpt-image-1":
        return response.json()["data"][0]["b64_json"]


def get_url_video_generate_by_neuroimg(
    url: str,
    api_key: str,
    prompt: str,
    model: str = "flux-schnell",
    width: int = 1024,
    heigh: int = 1024,
):
    """Возвращает url для скачивания изображения

    Работа с сайтом https://neuroimg.art

    Args:
        url (str): url генерации изображения
        api_key (str): API Key для доступа
        prompt (str): Описание изображения
        model (str, optional): модель генерации изображения
        width (int, optional): Ширина изображения
        heigh (int, optional): Высота изображения
    Returns:
        _type_: Возвращает url для скачивания изображения
    """

    data = {
        "token": api_key,
        "model": model,
        "prompt": prompt,
        "width": width,
        "heigh": heigh,
    }
    response = requests.post(url=url, json=data)

    return response.json().get("image_url", None)


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
    """Возвращает список, в котором содержится описания каждого найденного видео.

    Args:
        name_video (str): Имя видео
        sort (str): тип сортировки

    Returns:
        _type_: Возвращает список, в котором содержится описания каждого найденного видео
    """
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


def get_user_info(
    api_id: int,
    first_name: str,
    user_name: str,
    last_name: Optional[str],
) -> str:
    """Возвращает строку с информацией о пользователе.

    Args:
        api_id (int): Id пользователя телеграмма
        first_name (str): first_name пользователя
        user_name (str): username пользователя

    Returns:
        _type_: Возвращает строку с информацией о пользователе
    """
    user_json = (
        f"@{user_name}\nId: {hbold(api_id)}\nFirst name: {hbold(first_name)}\n"
        f"Last_name: {hbold(last_name)}\n"
    )

    return user_json


def get_proxies_by_webshare(
    url_config: str,
    url_proxeis_list: str,
    api_key: str,
    path_proxies: str,
    filename: str,
):
    """Возврщает строку с 10 прокси для сайта https://www.webshare.io/

    Args:
        url_config (str): url для получения данных о пользователе
        url_proxeis_list (str): url для получения списка  прокси
        api_key (str): Api ключ
        path_proxies (str): Относительный путь до файла
        filename (str): Имя файла

    Returns:
        _type_: Возврщает строку с 10 прокси
    """
    try:
        response = requests.get(
            url_config,
            headers={
                "Authorization": f"{api_key}",
            },
        )
    except Exception as err:
        print(err)
        return None

    token = response.json()["proxy_list_download_token"]

    response = requests.get(url=url_proxeis_list.format(token))

    proxies_list = response.text.split("\r\n")
    proxies_list.pop(-1)

    path = Path(__file__).parent

    full_path = os.path.join(path, path_proxies, filename)

    with open(full_path, "w", encoding="utf-8") as file:
        for proxy in proxies_list:
            ip, port, username, password = proxy.split(":")
            file.write(f"{username}:{password}@{ip}:{port}\n")

    with open(full_path, "r", encoding="utf-8") as file:
        proxies = file.read()

    return proxies


def get_ip_info(ip: str, url: str, acces_key: str):
    """Возвращает пользователю информацию по ip, из сайта http://api.ipapi.com.

    Args:
        ip (str): ip пользователя
        url (str): _description_
        acces_key (str): ключ доступа

    Returns:
        _type_: Возвращает пользователю информацию по ip
    """

    url = url.format(ip, acces_key)
    response = requests.get(url).json()
    flag = response.get("country_code")

    with open("file.json", "w") as file:
        json.dump(response, file, indent=4, ensure_ascii=False)

    path = Path(__file__).parent
    if flag:
        code = flag.lower()
        full_path = os.path.join(path, f"static/img/flag/{code}.png")
    else:
        full_path = os.path.join(path, f"static/img/none.png")
    data = (
        f"ip: {response.get('ip', None)}\nhostname: {response.get('hostname', None)}\n"
        f"type: {response.get('type', None)}\n"
        f"continent_code: {response.get('continent_code', None)}\n"
        f"continent_name: {response.get('continent_name', None)}\n"
        f"country_code: {response.get('country_code', None)}\n"
        f"country_name: {response.get('country_name', None)}\n"
        f"region_code: {response.get('region_code', None)}\n"
        f"region_name: {response.get('region_name', None)}\n"
        f"city: {response.get('city', None)}\n"
        f"zip: {response.get('zip', None)}\n"
        f"latitude: {response.get('latitude', None)}\n"
        f"longitude: {response.get('longitude', None)}\n"
        f"msa: {response.get('msa', None)}\n"
        f"dma: {response.get('dma', None)}\n"
        f"radius: {response.get('radius', None)}\n"
        f"ip_routing_typea: {response.get('ip_routing_typea', None)}\n"
        f"connection_type: {response.get('connection_type', None)}\n"
        f"geoname_id: {response['location'].get('geoname_id', None)}\n"
        f"capital: {response['location'].get('capital', None)}\n"
        f"country_flag_emoji: {response['location'].get('country_flag_emoji', None)}\n"
        f"country_flag_emoji_unicode: {response['location'].get('country_flag_emoji_unicode', None)}\n"
        f"calling_code: {response['location'].get('calling_code', None)}\n"
        f"is_eu: {response['location'].get('is_eu', None)}\n"
    )
    return full_path, data


def searches_for_videos_by_name_for_kinopoisk(
    name: str,
):
    """Возвращает json с найденными видео для сайта кинпоиск.

    Args:
        name (str): Имя видео

    Returns:
        _type_: Возвращает json с найденными видео для сайта кинпоиск
    """
    url: str = settings.recommender_system.kinopoisk.URL_SEARCH_VIDEO_NAME.format(
        10, name
    )

    HEADERS = {
        "accept": "application/json",
        "X-API-KEY": settings.recommender_system.kinopoisk.ApiKey,
    }

    response = requests.get(url=url, headers=HEADERS).json()
    return response


def get_recommender_video_for_kinopoisk(
    list_genres: List,
    limit: int,
    type_video: str,
    rating: str,
):
    """Возвращает список из словарей рекомендованных фильмов для кинопоиска.

    Args:
        list_genres (List): Список жанров фильма
        limit (int): Количество выдаваемых фильмов
        type_video (str): Тип видео
        rating: (str): Рейтинг видео

    Returns:
        _type_: Возвращает список из словарей рекомендованных фильмов для кинопоиска
    """
    # Создает случайный список из двух жанров в которых снят фильм
    array_genres = []
    for genre in list_genres:
        array_genres.append(genre.get("name"))
    if len(array_genres) > 1:
        array_genres = random.sample(array_genres, 2)

    url: str = settings.recommender_system.kinopoisk.URL_SEARCH_UNIVERSAL_VIDEO.format(
        limit
    )

    for genre in array_genres:
        url = url + f"&genres.name={genre}"

    HEADERS = {
        "accept": "application/json",
        "X-API-KEY": settings.recommender_system.kinopoisk.ApiKey,
    }

    url += f"&type={type_video}"
    url += f"&rating.kp={rating}"

    array_recommender = requests.get(url=url, headers=HEADERS).json().get("docs")

    return array_recommender


def get_description_video_from_kinopoisk(data: Dict) -> str:
    """Возвращает строку с описанием фильма для кинопоиска.

    Args:
        data (Dict): Словарь содержащий данные о фильме

    Returns:
        _type_: Возвращает строку с описанием фильма для кинопоиска
    """
    name = f'{data.get("name")}\n\n'

    array_genres = []
    for genre in data.get("genres"):
        array_genres.append(genre.get("name"))
    array_countries = []
    for country in data.get("countries"):
        array_countries.append(country.get("name"))
    if data.get("alternativeName", 0):
        name += f"Другое название: {data.get('alternativeName')}\n"
    if data.get("type", 0):
        name += f"Тип видео: {data.get('type')}\n"
    if data.get("year", 0):
        name += f"Год выхода: {data.get('year')}\n"
    if data.get("description", 0):
        descripton = f"{data['description'][:200]}...."
        name += f"Описание: {descripton}\n"
    if data.get("shortDescription", 0):
        name += f"Короткое описание: {data['shortDescription']}\n"
    if data.get("movieLength", 0):
        name += f"Длина фильма: {data['movieLength']} м.\n"
    if data["rating"].get("kp", 0):
        data_kp = data["rating"].get("kp")
        name += f"Рейтинг на кинпоиске: {data_kp}\n"
    if data["rating"].get("imdb", 0):
        data_imdb = data["rating"].get("imdb")
        name += f"Рейтинг на imdb: {data_imdb}\n"

    genres = ""
    if array_genres:
        genres: str = "Список жанров: "
        for g in array_genres:
            genres += f"{g},"
        genres = genres.strip(",")
    if genres:
        name += f"{genres}\n"

    countries = ""
    if array_countries:
        countries: str = "Страны: "
        for c in array_countries:
            countries += f"{c},"
        countries = countries.strip(",")
    if countries:
        name += f"{countries}\n"

    return name
