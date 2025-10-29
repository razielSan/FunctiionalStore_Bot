from typing import Optional, Dict
from pathlib import Path
import traceback

from aiogram.utils.markdown import hbold
import aiohttp

from settings.response import ResponseData
from settings.config import settings
from errors_handlers.main import error_handler_for_the_website
from logging_handler.main import error_logging


async def get_ip_info(
    url: str,
    path_folder_flag_country: Path,
    path_folder_none_flag_img: Path,
) -> ResponseData:
    """

    Возвращает пользователю информацию по ip, из сайта http://api.ipapi.com.

    Args:
        url (str): url для получения информации о ip
        path_folder_flag_country (Path): Путь до папки с флагами стран
        path_folder_none_flag_img (Path): Путь до изображения если флаг не найден

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
        # Получаем данные с сайта
        async with aiohttp.ClientSession() as session:
            response_ip: ResponseData = await error_handler_for_the_website(
                session=session,
                url=url,
            )

        if response_ip.error:
            return response_ip

        data_response_ip: Dict = response_ip.message

        # Получаем код страны если страна найденна
        country_code: str = data_response_ip.get("country_code", None)

        # Формируем путь до картинки с флагом страны если есть
        if country_code:
            code: str = country_code.lower()
            full_path: Path = path_folder_flag_country / f"{code}.png"
        else:
            full_path: Path = path_folder_none_flag_img

        # Составляем данные по ip
        data_ip: str = (
            f"ip: {data_response_ip.get('ip', None)}\n"
            "hostname: {data_response_ip.get('hostname', None)}\n"
            f"type: {data_response_ip.get('type', None)}\n"
            f"continent_code: {data_response_ip.get('continent_code', None)}\n"
            f"continent_name: {data_response_ip.get('continent_name', None)}\n"
            f"country_code: {data_response_ip.get('country_code', None)}\n"
            f"country_name: {data_response_ip.get('country_name', None)}\n"
            f"region_code: {data_response_ip.get('region_code', None)}\n"
            f"region_name: {data_response_ip.get('region_name', None)}\n"
            f"city: {data_response_ip.get('city', None)}\n"
            f"zip: {data_response_ip.get('zip', None)}\n"
            f"latitude: {data_response_ip.get('latitude', None)}\n"
            f"longitude: {data_response_ip.get('longitude', None)}\n"
            f"msa: {data_response_ip.get('msa', None)}\n"
            f"dma: {data_response_ip.get('dma', None)}\n"
            f"radius: {data_response_ip.get('radius', None)}\n"
            f"ip_routing_type: {data_response_ip.get('ip_routing_type', None)}\n"
            f"connection_type: {data_response_ip.get('connection_type', None)}\n"
            f"geoname_id: {data_response_ip['location'].get('geoname_id', None)}\n"
            f"capital: {data_response_ip['location'].get('capital', None)}\n"
            f"country_flag_emoji: {data_response_ip['location'].get('country_flag_emoji', None)}\n"
            f"country_flag_emoji_unicode: {data_response_ip['location'].get('country_flag_emoji_unicode', None)}\n"
            f"calling_code: {data_response_ip['location'].get('calling_code', None)}\n"
            f"is_eu: {data_response_ip['location'].get('is_eu', None)}\n"
        )
        return ResponseData(
            message=[str(full_path), data_ip],
            status=200,
            url=url,
            method="GET",
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


async def get_user_info(
    api_id: int,
    first_name: str,
    user_name: str,
    last_name: Optional[str],
) -> str:
    """

    Функция для получения информации о пользователе

    Args:
        api_id (int): Id telegram пользователя
        first_name (str): Имя пользователя
        user_name (str): Логин пользователя
        last_name (Optional[str]): Фамилия пользователя[По умолчанию None]

    Returns:
        str: Строка содержащая информацию о пользователе по api id telegram
    """

    # Формируем сообщение о пользователе
    user_json: str = (
        f"@{user_name}\nId: {hbold(api_id)}\nFirst name: {hbold(first_name)}\n"
        f"Last_name: {hbold(last_name)}\n"
    )

    return user_json
