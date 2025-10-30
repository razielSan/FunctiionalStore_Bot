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
    try:
        response = requests.post(url=url, json=data, timeout=10)
    except Exception as err:
        print(err)
        return None
    return response.json().get("image_url", None)


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


def create_video_by_is_vheer(
    url: str,
    driver_path: str,
    image_path: str,
    video_path: str,
    video_data: str,
    prompt: str,
    update_progress: Callable,
    cancel_chek: Callable,
    description_url: Optional[str] = None,
) -> Dict:
    """Заходит на сайт https://vheer.com, через  selenium, загружает описание
       изображений, жмет кнопку генерации видео и скачивае видео с сайта в папку

    Args:
        url (str): URL сайта vheer для генерации изображения
        driver_path (str): Путь для драйвера
        image_path (str): Путь до картинки с изображением
        video_path (str): Путь для сохранения изображения
        video_data (str): JavsSripts для сохранения видео через blob
        prompt (str): описание изображения
        update_progress (Callable): Функция для отслеживания прогресса скачивания
        cancel_chek (Callable): Функция для отмены генерации изорбражения

    Returns:
        Dict[str, str]: Возвращает словарь вида
        {'message': <путь до загруженого видео>} - если функция отработал успешно
        {'error': <сообщение об ошибке>} - если произошла ошибка
    """

    # 1 Обновляем прогресс при заходе в функцию
    update_progress()

    service: Service = Service(executable_path=driver_path)

    options: Options = Options()

    options.add_argument(
        r"user-data-dir=C:\Пользователи\Raz\AppData\Local\Google\Chrome\User Data"
    )
    options.add_argument(
        "profile-directory=Default"
    )  # или "Profile 1", если не основной

    # Добавляем user_agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36"
    )

    # 🚫 Отключаем флаги автоматизации
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 🔇 Убираем лишние логи
    options.add_argument("--log-level=3")

    # Режим без интерфейса
    options.add_argument("--headless=new")

    # Дополнительно, чтобы избежать лишних окон/уведомлений
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)
    # driver.set_window_size(1280, 800)

    # file_path = os.path.abspath("1.jpg")
    try:

        # 2 Обновляем прогресс(до загрузки сайта) для вывода пользователю
        update_progress()

        # Если есть URL для сайта с описанием изображения заходим в него
        if description_url:
            driver.get(description_url)
            print(1)
            prompt: str = get_prompt_for_image(
                driver=driver, image_path=image_path
            ).get("message")
            print(2)

        driver.get(url=url)

        # Проверяем на состояние отмены

        chek_cancel(selenium_driver=driver, cancel_chek=cancel_chek)

        # 3 Обновляем прогресс(когда сайт загрузился) для вывода пользователю
        update_progress()
    except Exception as err:
        print(err)
        return {"error": "Сайт не отвечает"}
    try:
        wait: WebDriverWait[WebElement] = WebDriverWait(driver, 60)

        # 4 Обновляем прогресс(до загрузки фото на сайт) для вывода пользователю
        update_progress()

        file_input: WebElement = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        abs_path: str = os.path.abspath(image_path)
        file_input.send_keys(abs_path)
        time.sleep(10)

        # Проверяем на состояние отмены
        chek_cancel(selenium_driver=driver, cancel_chek=cancel_chek)

        # 5 Обновляем прогресс(после загрузки фото на сайт загрузки сайта) для вывода пользователю
        update_progress()

        text_area: WebElement = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'textarea[placeholder^="Input image"]')
            )
        )
        text_area.clear()
        text_area.send_keys(prompt)
        time.sleep(2)

        # Ждём, пока overlay исчезнет (если есть блок Processing)
        try:
            wait.until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "div.absolute.inset-0.z-20")
                )
            )
        except Exception:
            pass  # если overlay нет — игнорируем

        # Ждём появления кнопки и кликабельности
        button_generate: WebElement = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//text()[contains(., 'Generate')]]")
            )
        )

        # Скроллим и кликаем через JS (надёжнее на Tailwind/React)
        driver.execute_script("arguments[0].scrollIntoView(true);", button_generate)
        driver.execute_script("arguments[0].click();", button_generate)
        time.sleep(2)

        # 6 Обновляем прогресс(после того когда кликнули кнопку сгенерировать видео) для вывода пользователю
        update_progress()

        # Ждём появления <video> — сайт сначала генерирует blob, поэтому даём запас времени
        video_el: WebElement = WebDriverWait(driver, 400).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.h-full.relative > video")
            )
        )

        # Проверяем на состояние отмены
        chek_cancel(selenium_driver=driver, cancel_chek=cancel_chek)

        # 7 Обновляем прогресс(после того когда видео сгенерировалось) для вывода пользователю
        update_progress()

        # settings.video_generation.vheer.VIDEO_DATA,

        # Достаём blob как base64 через JavaScript
        video_data: str = driver.execute_async_script(
            video_data,
            video_el,
        )

        if video_data.startswith("ERROR:"):
            return {"error": "Не удалось скачать видео: " + video_data}

        # Сохраняем base64 как mp4

        header, encoded = video_data.split(",", 1)
        binary_data: bytes = base64.b64decode(encoded)

        video_path: str = f"{video_path}{random.randint(0, 1000)}.mp4"

        # 8 Обновляем прогресс(до того когда сохранили видео в папку) для вывода пользователю
        update_progress()

        with open(video_path, "wb") as f:
            f.write(binary_data)

        # Проверяем на состояние отмены
        chek_cancel(selenium_driver=driver, cancel_chek=cancel_chek)

        # 9 Обновляем прогресс(когда сохранили видео в папку) для вывода пользователю
        update_progress()

        driver.close()
        return {"message": video_path}

    except Exception as err:
        print(err)
        traceback.print_exc()
        return {"error": "Ошибка при работа с сайтом"}
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def get_prompt_for_image(
    driver: webdriver.Chrome,
    image_path: str,
) -> Dict[str, str]:
    """Заходит на сайт "https://products.aspose.ai, загружает картинку, нажимает на кнопку сгенерировать
    описание и возвращает описание изображения

    Args:
        driver (_type_): драйвер для селениума с уже загруженым в нем сайтом https://products.aspose.ai
        image_path (str): путь до картинки для описания

    Returns:
        Dict[str, str]: Возвращает словарь вида
        {'message': <описание изображение>} - если функция отработал успешно
        {'error': <сообщение об ошибке>} - если произошла ошибка
    """
    try:
        wait: WebDriverWait = WebDriverWait(driver, 60)
        image_input: WebElement = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        path: str = os.path.abspath(image_path)
        image_input.send_keys(path)
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.ID, "description-lang")))
        Select(driver.find_element(By.ID, "description-lang")).select_by_value("en")

        time.sleep(2)
        generate_button: WebElement = wait.until(
            EC.presence_of_element_located((By.ID, "uploadButton"))
        )
        generate_button.click()

        text_area: WebElement = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "textarea[class='text-area']",
                )
            )
        )

        text: str = text_area.text.translate(str.maketrans("", "", "*-"))

        return {"message": text}
    except Exception as err:
        print(err)
        traceback.print_exc()
        return {"error": "Ошибка при работе с products.aspose.ai"}
