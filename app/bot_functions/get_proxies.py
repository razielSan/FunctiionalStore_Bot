import aiohttp
import traceback
from typing import Dict

from errors_handlers.main import error_handler_for_the_website
from settings.response import ResponseData
from logging_handler.main import error_logging
from settings.config import settings


async def get_proxies_by_webshare(
    url_config: str,
    url_proxeis_list: str,
    api_key: str,
) -> ResponseData:
    """
       Возврщает обьект ResponseData содержащий
       строку с 10 прокси для сайта https://www.webshare.io/

    Args:
        url_config (str): url для получения данных о пользователе
        url_proxeis_list (str): url для получения списка  прокси
        api_key (str): Api ключ

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
            # Делаем запрос на получение токена
            response_token: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url_config,
                headers={
                    "Authorization": f"{api_key}",
                },
            )

            if response_token.error:
                return response_token

            token: Dict = response_token.message[
                "proxy_list_download_token"
            ]  # Получаем токен

            # Делаем запрос на получение прокси адресов
            response_proxies: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url_proxeis_list.format(token=token),
                data_type="TEXT",
            )
            if response_proxies.error:
                return response_proxies
        # Получаем список из адресо прокси
        proxies_list: str = response_proxies.message.split("\r\n")
        proxies_list.pop(-1)


        # Формируем строки содержащиую адреса прокси 
        data: str = ""
        for proxy in proxies_list:
            ip, port, username, password = proxy.split(":")
            data += f"{username}:{password}@{ip}:{port}\n"

        return ResponseData(
            message=data,
            status=response_proxies.status,
            method=response_proxies.method,
            url=response_proxies.url,
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
