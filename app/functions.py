from typing import List
import random

import requests

from settings.config import settings


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
