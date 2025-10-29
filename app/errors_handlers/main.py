import json

import aiohttp
import asyncio
import traceback

from logging_handler.main import error_logging
from settings.response import ResponseData
from settings.config import settings


async def safe_read_response(resp):
    """Проверяет в каком формате был передан ответ с сайта и возвращает текст ответа

    Args:
        resp (_type_): запрос для сайта

    Returns:
        _type_: Возвращает содержание текста ответа с сайта
    """
    try:
        content_type = resp.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            data = await resp.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        return await resp.text()
    except Exception:
        return "<no body>"


async def error_handler_for_the_website(
    session,
    url: str,
    data_type="JSON",
    timeout=20,
    method="GET",
    data=None,
    headers=None,
) -> ResponseData:
    """

    Асинхронный запрос с обработками ошибок для сайтов

    Args:
        session (_type_): асинхронная сессия запроса
        url (_type_): URL сайта
        data_type (str, optional): Тип возвращаемых данных.По умолчанию JSON('JSON', 'TEXT', 'BYTES')
        timeout (int, optional): таймаут запроса в секундах
        method (str, optional): Метод запроса. 'POST' или "GET"
        data (_type_, optional): Данные для POST запроса
        headers (dict): Заголовки запроса

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    # Чтобы не ждать бесконечно при connect/read
    timeout_cfg: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=timeout)

    try:
        async with session.request(
            method,
            url,
            timeout=timeout_cfg,
            data=data,
            headers=headers,
        ) as resp:
            if resp.status == 403:
                error_body = await safe_read_response(resp=resp)
                error_logging.error(
                    msg=settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                        method=method,
                        status=resp.status,
                        url=resp.url,
                        error_message=error_body[:500],
                    )
                )

                return ResponseData(
                    status=resp.status,
                    error="Доступ к сайту запрещен",
                    url=url,
                    method=method,
                )
            if resp.status != 200:
                error_body = await safe_read_response(resp=resp)
                error_logging.error(
                    msg=settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                        method=method,
                        status=resp.status,
                        url=resp.url,
                        error_message=error_body[:500],
                    )
                )
                return ResponseData(
                    status=resp.status,
                    error=f"Сайт вернул ошибку {resp.status}",
                    url=url,
                    method=method,
                )
            if data_type.upper() == "JSON":
                message_body = await resp.json()
                return ResponseData(
                    message=message_body,
                    status=resp.status,
                    url=url,
                    method=method,
                )
            elif data_type.upper() == "TEXT":
                message_body = await resp.text()
                return ResponseData(
                    message=message_body,
                    status=resp.status,
                    url=url,
                    method=method,
                )
            else:
                message_body = await resp.read()
                return ResponseData(
                    message=message_body,
                    status=resp.status,
                    url=url,
                    method=method,
                )
    except aiohttp.ClientError:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method=method,
                status=0,
                url=url,
                error_message=traceback.format_exc(),
            )
        )
        return ResponseData(
            error="Не удалось подлкючиться к сайтy",
            status=0,
            url=url,
            method=method,
        )
    except asyncio.TimeoutError:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method=method,
                status=0,
                url=url,
                error_message=traceback.format_exc(),
            )
        )
        return ResponseData(
            error="Время ожидания истекло",
            status=0,
            url=url,
            method=method,
        )
    except Exception:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE.format(
                method=method,
                status=0,
                url=url,
                error_message=traceback.format_exc(),
            )
        )
        return ResponseData(
            error="Ошибка на стороне сервера.Идет работа по исправлению...",
            status=0,
            url=url,
            method=method,
        )


def chek_number_is_positivity(number: str):
    """

    Проверяет является ли входящее  значение положительным числом

    Args:
        number (str): Данные для проверки

    Returns:
        ResponseData: Возвращает экземпляр класса ResponseData

        Атрибуты ResponseData:
            - message (Any | None): Само число если оно прошло проверку.
            - error (str | None): Описание ошибки, если число не прошло проверку.
    """

    try:
        number: int = int(number)
        if number <= 0:
            return ResponseData(error="Число должно быть больше 0")
        return ResponseData(message=number)
    except Exception:
        return ResponseData(error="Данные должны быть целым числом")
