from typing import Dict, List, Optional
import os
import traceback
import aiohttp
from aiogram.types import Message
import asyncio
from concurrent.futures import ThreadPoolExecutor
from asyncio import AbstractEventLoop, Task

from icrawler.builtin import BingImageCrawler

from logging_handler.main import error_logging
from errors_handlers.main import error_handler_for_the_website
from settings.response import ResponseData
from settings.config import settings


async def find_image_with_goole_and_save_image(
    name: str,
    count: int,
    filters: Dict,
    path: str,
    message: Message,
) -> ResponseData:
    """Ищет картинки в google.com и сохраняет их.

    Args:
        name (str): Имя картинки
        count (int): Количество изображений для скачивания
        filters (Dict): Фильтры для изображения
        path (str): Путь куда будут залиты изображения
        message: (Message): Тип сообщения для aiogram

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
        # Чтобы избежать UnboundLocalError
        response: Optional[ResponseData] = None

        # Проверяем доступен ли сайт с помощью которого будем скачивать
        # картинки
        async with aiohttp.ClientSession() as session:
            response: Dict = await error_handler_for_the_website(
                session=session,
                url="https://www.google.com/",
                data_type="TEXT",
            )
            if response.error:
                return response

        # Количество скаченных картинок
        crawler_download: int = 0

        # Формируем сообщения для отслеживания прогресса
        status_message: Message = await message.answer(
            f"📸 Загружено: {crawler_download} из {count}..."
        )

        crawler: BingImageCrawler = BingImageCrawler(storage={"root_dir": path})

        loop: AbstractEventLoop = asyncio.get_event_loop()
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)

        async def run_crowl() -> None:
            await loop.run_in_executor(
                executor,
                lambda: crawler.crawl(
                    keyword=name,
                    max_num=count,
                    filters=filters,
                ),
            )

        crawl_task: Task[None] = asyncio.create_task(run_crowl())

        # Отображаем прогресс скачивания для пользователя
        last_count: int = 0
        while not crawl_task.done():
            await asyncio.sleep(1)
            crawler_download = sum(len(files) for _, _, files in os.walk(path))
            if crawler_download != last_count:
                try:
                    await status_message.edit_text(
                        f"📸 Загружено: {crawler_download} из {count}..."
                    )
                    last_count = crawler_download
                except Exception:
                    traceback.print_exc()
                    pass

        await crawl_task

        if not crawler_download:
            return ResponseData(
                error="Не найденно ни одного изображения",
                status=404,
                url=getattr(response, "url", "<unknown>"),
                method=getattr(response, "method", "TEXT"),
            )

        await status_message.edit_text(
            f"✅ Готово! Загружено {crawler_download} изображений."
        )
        return ResponseData(
            message=crawler_download,
            status=200,
            url=response.url,
            method=response.method,
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


async def get_url_link_posters_for_kinopoisk(
    list_url: List, headers: Dict, message: Message
) -> ResponseData:
    """

    Возвращает обьект класса ResponseData, содержащий список с url ссылками
    на фото постеров и именами для фильмов с сайта кинопоиск.

    Args:
        list_url (List): Cписок с URL для сайта кипоиск
        headers (Dict): Заголовок должен быть вида
        { "accept": "application/json","X-API-KEY": <api_key>,}
        message (Message): message библиотеки aiogram

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
        array_link_img_url: List = []

        # Делаем оторбажения прогресс скачивания
        download: int = 0
        count: int = len(list_url)
        msg: str = "📸 Полученно ссылок {} из {}..."
        status_message: Message = await message.answer(
            text=msg.format(
                download,
                count,
            )
        )

        # Чтобы избежать UnboundLocalError
        poster_response: Optional[ResponseData] = None
        async with aiohttp.ClientSession() as session:
            for url in list_url:
                # Делаем запрос на получени постера для фильма
                poster_response: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=url,
                    headers=headers,
                )
                if poster_response.error:
                    return poster_response
                link_img_url: str = poster_response.message["docs"][0]["poster"]["url"]
                # Если постер существует для фильма
                if link_img_url:
                    # Обновляем прогресс скачивания
                    download += 1
                    if download % 2 == 0 or download == count:
                        await status_message.edit_text(
                            msg.format(
                                download,
                                count,
                            )
                        )

                    array_link_img_url.append(
                        [
                            link_img_url,
                            poster_response.message["docs"][0]["name"],
                        ]
                    )
        if not array_link_img_url:
            return ResponseData(
                error="Постеры для фильмов не найденны",
                status=404,
                url=getattr(poster_response, "url", "<unknown>"),
                method=getattr(poster_response, "method", "GET"),
            )
        return ResponseData(
            message=array_link_img_url,
            status=200,
            url=poster_response.url,
            method=poster_response.method,
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
