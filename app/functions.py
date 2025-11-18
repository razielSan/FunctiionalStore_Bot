from typing import Dict, Optional, List, Callable
import os
import sys
import json
from pathlib import Path
import base64
import random
import time
import traceback

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from settings.config import settings
from utils.generate_video import chek_cancel


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
        250
    )

    for genre in array_genres:
        url = url + f"&genres.name={genre}"

    HEADERS = {
        "accept": "application/json",
        "X-API-KEY": settings.recommender_system.kinopoisk.ApiKey,
    }

    url += f"&type={type_video}"
    url += f"&rating.kp={rating}"

    array_recommender = (
        requests.get(
            url=url,
            headers=HEADERS,
            timeout=15,
        )
        .json()
        .get("docs")
    )
    random.shuffle(array_recommender)

    return array_recommender[:limit]


def get_description_video_from_kinopoisk(data: Dict) -> str:
    """Возвращает строку с описанием фильма для кинопоиска.

    Args:
        data (Dict): Словарь содержащий данные о фильме

    Returns:
        _type_: Возвращает строку с описанием фильма для кинопоиска
    """
    name = f'{data.get("name")}\n\n'

    array_genres = []
    if data.get("genres", 0):
        for genre in data.get("genres"):
            array_genres.append(genre.get("name"))
    array_countries = []
    if data.get("countries", 0):
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
