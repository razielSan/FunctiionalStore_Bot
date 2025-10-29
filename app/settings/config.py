from typing import List, Dict
from pathlib import Path
from typing import Optional

from pydantic_settings import SettingsConfigDict, BaseSettings
from aiogram.types import BotCommand
from pydantic import BaseModel

from settings import path_settings


# Модели для генерации изображений


class PollinationsImageGeneration(BaseModel):
    """Модель сайта https://pollinations.ai/."""

    IMAGE_GENERATE: str = (
        "https://image.pollinations.ai/prompt/{}"  # URL для генерации изображений
    )


class CailaIoImageGeneration(BaseModel):
    """Модель сайта https://caila.io/."""

    ApiKey: Optional[str] = None
    URL_IMAGE_GENERATE: str = "https://caila.io/api/adapters/openai/images/generations"


class NeuroimgImageGeneration(BaseModel):
    """Модель сайта https://neuroimg.art/."""

    ApiKey: Optional[str] = None
    URL_IMAGE_GENERATE: str = "https://neuroimg.art/api/v1/free-generate"


class ImageGeneration(BaseModel):
    """Модели для генерации изображений по описанию."""

    pollinations: PollinationsImageGeneration = PollinationsImageGeneration()
    caila: CailaIoImageGeneration = CailaIoImageGeneration()
    neuroimg: NeuroimgImageGeneration = NeuroimgImageGeneration()


# Модели для генераци описаний изображений


class ImaggaImageDescription(BaseModel):
    """Модель сайта https://imagga.com/."""

    AUTHORIZATION: Optional[str] = None  # Токен аторизации
    UPLOAD_ENDPOINT: str = "https://api.imagga.com/v2/uploads"  # URL для получения uplooad_image_id картинки
    URL_TAGS: str = "https://api.imagga.com/v2/tags"  # URL для описание изображения


class ImageDescription(BaseModel):
    """Модели для описания изображений."""

    immaga: ImaggaImageDescription = ImaggaImageDescription()
    PATH_TO_IMAGE_DESCRIPTON: Path = (
        path_settings.APP_DIR
        / "static"
        / "img"
        / "image_description"  # путь до папки с картинками описаний изображений
    )


# Модели для поиска видео


class YoutubeAPI(BaseModel):
    """Модель для сайта https://www.youtube.com."""

    YoutubeApiKey: Optional[str] = None
    VIDEO_URL: str = "https://www.youtube.com/watch?v={}"
    CHANNEL_URL: str = "https://www.youtube.com/channel/{}"


class FindVideo(BaseModel):
    """Источники поиска видео."""

    youtube: YoutubeAPI = YoutubeAPI()


# Модели для получения прокси


class WebshareProxies(BaseModel):
    """Модель для сайта "https://www.webshare.io/."""

    ApiKey: Optional[str] = None
    PATH: str = "static/files/webshare/"
    URL_CONFIG: str = "https://proxy.webshare.io/api/v2/proxy/config/"  # url для получения данных о пользователе
    URL_PROXIES_LIST: str = "https://proxy.webshare.io/api/v2/proxy/list/download/{token}/-/any/username/direct/-/"  # url для получения списка  прокси


class Proxies(BaseModel):
    """Модели для получения прокси."""

    webshare: WebshareProxies = WebshareProxies()


# Модели для сбора информации по ip


class IpapiIpInfo(BaseModel):
    """Модель для сайта http://api.ipapi.com."""

    AccessKey: Optional[str] = None
    ULR_IP_INFO: str = "http://api.ipapi.com/api/{ip}?access_key={access_key}&hostname=1"  # url для получения информации о ip


class IpInfo(BaseModel):
    """Модели для сбора информации по ip."""

    ipapi: IpapiIpInfo = IpapiIpInfo()
    PATH_FOLDER_FLAG_COUNTRY: Path = (
        path_settings.APP_DIR / "static" / "img" / "flag"
    )  # Путь до папки с флагами стран
    PATH_FOLDER_NONE_FLAG_IMG: Path = (
        path_settings.APP_DIR / "static" / "img" / "none.png"
    )  # Путь до изображения если флага нет


# Модели для рекомендательной системы


class KinopoiskRecommenderSystem(BaseModel):
    """Модель рекомендательной системы для кинопоиска."""

    ApiKey: Optional[str] = None
    URL_SEARCH_VIDEO_NAME: str = (
        "https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit={}&query={}"
    )
    URL_SEARCH_UNIVERSAL_VIDEO: str = (
        "https://api.kinopoisk.dev/v1.4/movie?page=1&limit={}"
    )

    HEADERS: Dict = {
        "accept": "application/json",
        "X-API-KEY": None,
    }


class RecommenderSystem(BaseModel):
    """Модели рекомендательных систем."""

    kinopoisk: KinopoiskRecommenderSystem = KinopoiskRecommenderSystem()


# Модели для генерации паролей


class PasswordGeneration(BaseModel):
    """Класс для конфигурации генерации паролей."""

    simple: str = "simple"
    difficult: str = "difficult"
    keyboard_layout_english: List = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm",
        "qazwsxedcrfvtgbyhnujm",
    ]
    digit: str = "0123456789"


# Модели для генерации видео


class VheerVideoGeneration(BaseModel):
    """Модель генерации изображений для сайта https://vheer.com/."""

    TOTAL_STEP: int = (
        10  # Общее количество шагов для отслеживания прогресс загрузки видео
    )
    CALLBACK_INLINE_BUTTON: str = "vheer"  # callback запись в инлайн клавиатуре
    VIDEO_URL: str = "https://vheer.com/app/image-to-video"
    PROMPT_IMG_URL: str = (
        "https://products.aspose.ai/pdf/ru/image-description"  # URL для сайта по
    )
    # генерации описание по фаото

    VIDEO_DATA: str = """
        const video = arguments[0];
        const done = arguments[1];
        fetch(video.src)
            .then(r => r.blob())
            .then(blob => {
            const reader = new FileReader();
            reader.onload = () => done(reader.result);
            reader.readAsDataURL(blob);
            })
            .catch(err => done('ERROR:' + err.message));
        """  # JavaScripts для загрузки видео


class VideoGeneration(BaseModel):
    """Модель для генерации видео."""

    vheer: VheerVideoGeneration = VheerVideoGeneration()


# Модель для логирования
class LoggingSettings(BaseModel):
    """Модель для логгирования."""

    PATH_DATA_LOGGING: Path = (
        path_settings.APP_DIR / "logging_handler" / "data.log"
    )  # путь до файл с общим логгированием
    PATH_ERRORS_LOGGING: Path = (
        path_settings.APP_DIR / "logging_handler" / "errors.log"
    )  # путь до файла с логгированием ошибок
    FORMAT_FILE: str = (
        "[%(asctime)s] - %(module)s:%(lineno)s - [%(levelname)s - %(message)s]"
    )
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    ERROR_WEB_RESPONSE_MESSAGE: str = (
        "[{method}] {status} {url} -> {error_message}"  # Формат сообщения для ошибки в запросах.
    )
    # method, status, url, error_message


# Модель для поиска картинок
class FindImage(BaseModel):
    """Модель для поиска картинок"""

    PATH_FIND_IMAGE: Path = path_settings.APP_DIR / "static" / "img" / "find_image"


class Settings(BaseSettings):
    """Настройки бота."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    BASE_DIR: Path = Path(__file__).resolve().parent

    TOKEN: str
    BOT_COMMAND: List[BotCommand] = [
        BotCommand(
            command="/start",
            description="Вызов меню бота",
        )
    ]  # Список коммнад для бота
    API_OPENWEATHERMAP: str  # API для сайта https://api.openweathermap.org
    ULR_GEOLOCATED_OPENWEATHERMAP: str = "http://api.openweathermap.org/geo/1.0/direct?q={}&limit=5&appid={}"  # URL для получения геолокации
    URL_CURRENT_OPENWEATHERMAP: str = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"  # URL для текущего прогноза погоды
    URL_FEATURE_OPENWEATHERMAP: str = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"  # URL для прогноза погоды на 5 дней
    URL_WEATHER_MAPS: str = "https://tile.openweathermap.org/map/temp_new/0/0/0.png?appid={}"  # URL для получения карт погоды
    URL_AIR_POLLUTION: str = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}"  # URL для получения данных о загрязнении воздуха
    PATH_TO_WEATHER_TRANSLATION: Path = (
        path_settings.APP_DIR
        / "static"
        / "files"
        / "openweathermap"
        / "weather_translations.json"
    )  # Путь для файла с переводами описаний прогноза погоды на русский язык
    PATH_TO_WEATHER_MAP: Path = (
        path_settings.APP_DIR / "static" / "files" / "openweathermap"
    )  # Путь до папки для сохранения карты прогноза погоды
    WEATHER_INDICATORS: Dict = {
        "pressure": {
            "name": "Давление",
            "unit": "гПа",
            "emoji": "📊",
            "levels": {
                "low": ["низкое", "⬇️"],
                "normal": ["нормальное", "🟢"],
                "high": ["высокое", "⬆️"],
            },
        },
        "humidity": {
            "name": "Влажность",
            "unit": "%",
            "emoji": "💧",
            "levels": {
                "dry": ["сухо", "🏜️"],
                "comfortable": ["комфортно", "😊"],
                "humid": ["влажно", "💦"],
            },
        },
        "visibility": {
            "name": "Видимость",
            "unit": "м",
            "emoji": "👁️",
            "levels": {
                "excellent": ["отличная", "🔭"],
                "good": ["хорошая", "👀"],
                "poor": ["плохая", "🕶️"],
                "fog": ["туман", "🌫️"],
            },
        },
        "wind": {
            "name": "Ветер",
            "unit": "м/с",
            "emoji": "🌬️",
            "levels": {
                "calm": ["штиль", "🍃"],
                "light": ["лёгкий", "🌬️"],
                "moderate": ["умеренный", "💨"],
                "strong": ["сильный", "🌪️"],
                "storm": ["шторм", "🌀"],
            },
        },
        "clouds": {
            "name": "Облачность",
            "unit": "%",
            "emoji": "☁️",
            "levels": {
                "clear": ["ясно", "☀️"],
                "few": ["малооблачно", "🌤️"],
                "scattered": ["переменная", "⛅"],
                "broken": ["значительная", "☁️"],
                "overcast": ["пасмурно", "☁️🌧️"],
            },
        },
    }
    AIR_POLLUTION: Dict = {
        "so2": {
            "Хороший": [0, 20],
            "Справедливый": [20, 80],
            "Умеренный": [80, 250],
            "Бедный": [250, 350],
            "Очень плохо": [350, float("inf")],
            "translation": "диоксид серы",
            "emoji": "⚗️",
        },
        "pm10": {
            "Хороший": [0, 20],
            "Справедливый": [20, 50],
            "Умеренный": [50, 100],
            "Бедный": [100, 200],
            "Очень плохо": [200, float("inf")],
            "translation": "крупные частицы пыли",
            "emoji": "💨",
        },
        "pm2_5": {
            "Хороший": [0, 10],
            "Справедливый": [10, 25],
            "Умеренный": [25, 50],
            "Бедный": [59, 75],
            "Очень плохо": [75, float("inf")],
            "translation": "мелкодисперсные частицы",
            "emoji": "🌫️",
        },
        "o3": {
            "Хороший": [0, 60],
            "Справедливый": [60, 100],
            "Умеренный": [100, 140],
            "Бедный": [140, 180],
            "Очень плохо": [180, float("inf")],
            "translation": "озон",
            "emoji": "☀️",
        },
        "co": {
            "Хороший": [0, 4400],
            "Справедливый": [4400, 9400],
            "Умеренный": [9400, 12400],
            "Бедный": [12400, 15400],
            "Очень плохо": [15400, float("inf")],
            "translation": "оксид углерода",
            "emoji": "🔥",
        },
        "no2": {
            "Хороший": [0, 40],
            "Справедливый": [40, 70],
            "Умеренный": [70, 150],
            "Бедный": [150, 200],
            "Очень плохо": [200, float("inf")],
            "translation": "диоксид азота",
            "emoji": "🚗",
        },
    }  # Словарь с данными о компонентах загрязнения воздуха

    LOCATION_WEATHER: List[float] = [
        55.751244,
        37.618423,
    ]  # Список координат для города Москва
    WEATHER_LAYERS: Dict = {
        "Температура": "temp_new",
        "Облака": "clouds_new",
        "Осадки": "precipitation_new",
        "Давление": "pressure_new",
        "Ветер": "wind_new",
    }  # Список погодных слоёв OpenWeatherMap
    AQI: Dict = {
        1: "Хороший",
        2: "Удовлетворительный",
        3: "Средний",
        4: "Плохой",
        5: "Очень плохой",
    }  # Словарь индексов качества воздуха
    PATH_COOGLE_DRIVER: str = (
        "static\\browser_drivers\\chromedriver_109\\chromedriver.exe"
    )
    VIDEO_GENERATE_IMAGE_PATH: str = "static\\img\\generate_video\\"  # путь для сохранения картинки скидываемой пользователем
    # для генерации видео
    VIDEO_GENERATE_VIDEO_PATH: str = (
        "static\\video\\generate_video\\"  # Путь для сохранения сгенерируемого видео
    )

    find_image: FindImage = FindImage()
    modelimage: ImageGeneration = ImageGeneration()
    image_description: ImageDescription = ImageDescription()
    find_video: FindVideo = FindVideo()
    proxies: Proxies = Proxies()
    ip_info: IpInfo = IpInfo()
    recommender_system: RecommenderSystem = RecommenderSystem()
    password_generation: PasswordGeneration = PasswordGeneration()
    video_generation: VideoGeneration = VideoGeneration()
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
