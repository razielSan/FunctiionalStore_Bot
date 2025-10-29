from typing import Optional, List, Dict
import asyncio
import traceback

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from settings.response import ResponseData
from logging_handler.main import error_logging

from settings.config import settings


async def get_description_video_by_youtube(
    name_video: str,
    sort: str,
    api_key: str,
    youtube_video_url: str,
    youtube_channel_url: str,
    max_results: int = 50,
    relevance_language: str = "ru",
) -> ResponseData:
    """
    Ищет видео по имени для сайта youtube. Возвращает обьект ResponseData содержащий
    список с данными.

    Args:
        name_video (str): Имя видео
        sort (str): тип сортировки
        api_key (str): API ключ для youtube
        youtube_video_url (str): URL поиска видео
        youtube_channel_url (str): URL поиска по каналам
        max_results: int(): Количество результатов для поиска
        relevance_language: (str): Язык наиболее релевантный для выдачи ответов

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
        service = build(
            "youtube",
            "v3",
            developerKey=api_key,
        )

        type_youtube: str = (
            "channel" if sort == "channel" else "video"
        )  # Определяем тип сортировки
        order_youtube: Optional[str] = (
            None if sort == "channel" else sort
        )  # Определяем критерии сортировки

        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        response_youtube: Dict = await loop.run_in_executor(
            None,
            lambda: service.search()
            .list(
                q=name_video,
                part="snippet",
                relevanceLanguage=relevance_language,
                type=type_youtube,
                maxResults=max_results,
                order=order_youtube,
            )
            .execute(),
        )

        response_youtube: Optional[List] = response_youtube.get("items", None)

        if not response_youtube:
            return ResponseData(
                error="Не найденно ни одного видео",
                status=200,
                method="GET",
                url="https://www.youtube.com/",
            )

        array_video_description: List = []
        order: int = 0
        # Проходимся по списку с ответами для youtube
        for result in response_youtube:
            order += 1  # Номер описания видео
            video_id: str = result["id"].get("videoId", None)
            channel_id: str = result["id"].get("channelId", None)

            if video_id:
                url: str = youtube_video_url.format(video_id)
                template: str = f"Ссылка на видео\n{url}"

            else:
                url: str = youtube_channel_url.format(channel_id)
                template: str = f"Ссылка на канал\n{url}"

            # Формируем описание для видео
            title: str = result["snippet"]["title"].replace("&quot;", " ")
            description: str = result["snippet"]["description"].replace("&quot;", " ")

            array_video_description.append(
                f"{order}. {title}\n\n{description}\n\n{template}\n"
            )

        return ResponseData(
            message=array_video_description,
            status=200,
            method="GET",
            url="https://www.youtube.com/",
        )

    except HttpError as err:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method="GET",
                status=err.status_code,
                url="https://www.youtube.com/",
                error_message=f"Youtube API error: {err.reason}",
            )
        )
        error_logging.error()
        return ResponseData(
            error="Ошибка при доступе к youtube",
            status=err.status_code,
            method="GET",
            url="https://www.youtube.com/",
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
