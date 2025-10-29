from typing import List, Optional
import shutil
from pathlib import Path
import os
import traceback
import zipfile
import aiohttp
from aiogram.types import Message
import time

from logging_handler.main import error_logging
from errors_handlers.main import error_handler_for_the_website
from settings.response import ResponseData
from settings.config import settings


def get_list_images_name(
    count_images: int,
    path_find_image: Path,
) -> List:
    """Возвращает список путей к картинкам с названиями начинающимся с 000001.jpg

    Args:
        count_images (int): количество картинок
        path_find_image (Path): путь до изображения

    Returns:
        List: Возвращает список с путями для картинок
    """
    list_images_name: List = []
    for number in range(1, count_images + 1):
        # Путь до картинки
        path_image: Path = path_find_image / f"{number:06}.jpg"
        list_images_name.append(str(path_image))
    return list_images_name


def delete_images_and_archive(
    path_folder: Path,
    delete_folder: bool = True,
):
    """Удаляет все что есть в папке.

    Args:
        path_folder (Path): Путь до папки
        deleter_folder: (Path): Флаг для удаления папки(True для удаления, False оставить)
    """

    for filename in os.listdir(path_folder):
        filepath: str = os.path.join(path_folder, filename)
        try:
            if os.path.isfile(filepath) or os.path.islink(filepath):
                os.remove(filepath)
        except Exception:
            error_logging.error(traceback.format_exc())
            traceback.print_exc()

    if delete_folder:
        # Логика удаления папки с повторными попытками если занята
        if os.path.exists(path_folder):
            for _ in range(10):
                try:
                    shutil.rmtree(path_folder)
                    return
                except PermissionError:
                    time.sleep(1)  # подождать перед повтором
                except Exception:
                    traceback.print_exc()

        # Провереям если папка еще осталась
        if os.path.exists(path_folder):
            error_logging.error(msg=f"Не удалось удалить - {path_folder}")


def save_images_with_zip_archive(
    path_folder: Path,
    path_archive: Path,
    list_images_name: List,
):
    """Сохраняет изображения в zip архив.

    Args:
        path_folder (Path): Путь до папки
        path_archive (Path): Путь до архива
        list_images_name (List): Список с путями изображений
    """
    if not os.path.exists(path_folder):
        os.mkdir(path_folder)

    with zipfile.ZipFile(path_archive, "w", zipfile.ZIP_DEFLATED) as file:
        try:
            for file_path in list_images_name:
                file.write(file_path, arcname=os.path.basename(file_path))
        except Exception:
            error_logging.error(traceback.format_exc())
            traceback.print_exc()


async def save_images(
    list_url: List[List],
    path: Path,
    message: Message,
) -> ResponseData:
    """Сохраняет картинки из url в папку и возращает обьект класса ResponseData
       содержащий списк путей к изображениям

    Args:
        list_url (List): Список содержащий URL ссылки на изображения и имя файла
        path (Path): Путь до папки с изображениями для скачивания
        message (Message): тип сообщения aiogramm

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

        async with aiohttp.ClientSession() as session:
            msg: str = "📸 Скаченно изображений {} из {}..."
            total_count: int = len(list_url)
            count: int = 0
            final_list_path_img: List = []

            status_message: Message = await message.answer(
                text=msg.format(0, total_count)
            )

            if not os.path.exists(path=path):
                os.mkdir(path)

            for url, name in list_url:
                response: ResponseData = await error_handler_for_the_website(
                    session=session,
                    url=url,
                    data_type="BYTES",
                )

                if response.error:
                    continue
                count += 1

                path_img: Path = path / f"{name}.jpg"
                with open(path_img, "wb") as file:
                    file.write(response.message)
                final_list_path_img.append(path_img)

                if count % 2 == 0 or count == total_count:
                    await status_message.edit_text(
                        msg.format(
                            count,
                            total_count,
                        )
                    )

        if not final_list_path_img:
            return ResponseData(
                error="Не удалось скачать ни одного изображения",
                status=404,
                url=getattr(response, "url", "<unknown>"),
                method=getattr(response, "method", "BYTES"),
            )

        return ResponseData(
            message=final_list_path_img,
            status=200,
            url=response.url,
            method=response.method,
        )
    except Exception:
        error_logging.error(
            settings.logging.ERROR_WEB_RESPONSE_MESSAGE(
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
