from typing import List
from pathlib import Path
import traceback
import aiohttp

from errors_handlers.main import error_handler_for_the_website

from settings.config import settings
from logging_handler.main import error_logging
from settings.response import ResponseData


async def get_image_description_by_immaga(
    key_autorization: str,
    upload_endpoint: str,
    url_tags: str,
    path_img: Path,
    language="en",
    limit=-1,
) -> ResponseData:
    """Получает описание картинки для сайта https://imagga.com/.

    Args:
        key_autorization (str): Токен аторизации
        upload_endpoint (str): URL для получения uplooad_image_id картинки
        url_tags (str): URL для описание изображения
        path_img: (Path): Путь до картинки для описания изображений
        language (str, optional): Язык описания изображений.По умолчанию английский
        limit (int, optional): Количество описаний.По умолчанию максимальное

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
        async with aiohttp.ClientSession() as session:
            # Отправляем картинку на сайт для ее описания
            with open(path_img, "rb") as file:
                response: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=upload_endpoint,
                    headers={
                        "Authorization": f"Basic {key_autorization}",
                    },
                    data={"image": file},
                    method="POST",
                )

            if response.error:
                return response

            # Получаем upload_id картинки
            upload_id: str = response.message["result"]["upload_id"]

            # Делаем запрос на получение описание изображения
            response_image_description: ResponseData = (
                await error_handler_for_the_website(
                    session=session,
                    url=f"{url_tags}?image_upload_id="
                    f"{upload_id}&language={language}&limit={limit}",
                    headers={
                        "Authorization": f"Basic {key_autorization}",
                    },
                )
            )

            if response_image_description.error:
                return response_image_description

        # Формируем данные для описания картинки
        array_image_description: List = [
            "Список возможных вариантов изображения на картинке:\n\n"
        ]

        for data in response_image_description.message["result"]["tags"]:
            array_image_description.append(
                f"{data['tag'][language].title()} ({data['confidence']:.3f}%) "
            )

        mess: str = "\n".join(array_image_description)
        return ResponseData(
            message=mess,
            status=200,
            method=response_image_description.method,
            url=response_image_description.url,
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
