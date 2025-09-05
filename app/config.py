from typing import List, Dict

from typing import Optional

from pydantic_settings import SettingsConfigDict, BaseSettings
from aiogram.types import BotCommand
from pydantic import BaseModel


class PollinationsImageGeneration(BaseModel):
    """Модель сайта https://pollinations.ai/."""

    IMAGE_GENERATE: str = (
        "https://image.pollinations.ai/prompt/{}"  # URL для генерации изображений
    )


class CailaIoImageGeneration(BaseModel):
    """Модель сайта https://caila.io/."""

    ApiKey: Optional[str] = None
    URL_IMAGE_GENERATE: str = "https://caila.io/api/adapters/openai/images/generations"


class ImaggaImageDescription(BaseModel):
    """Модель сайта https://imagga.com/."""

    AUTHORIZATION: Optional[str] = None  # Токен аторизации
    UPLOADEN_ENDPOINT: str = "https://api.imagga.com/v2/uploads"  # URL для получения uplooad_image_id картинки
    URL_TAGS: str = "https://api.imagga.com/v2/tags?"  # URL для описание изображения


class YoutubeAPI(BaseModel):
    YoutubeApiKey: Optional[str] = None
    VIDEO_URL: str = "https://www.youtube.com/watch?v={}"
    CHANNEL_URL: str = "https://www.youtube.com/channel/{}"


class ImageGeneration(BaseModel):
    """Модели для генерации изображений по описанию."""

    pollinations: PollinationsImageGeneration = PollinationsImageGeneration()
    caila: CailaIoImageGeneration = CailaIoImageGeneration()


class ImageDescription(BaseModel):
    """Модели для описания изображений."""

    immaga: ImaggaImageDescription = ImaggaImageDescription()


class FindVideo(BaseModel):
    """Источники поиска видео."""

    youtube: YoutubeAPI = YoutubeAPI()


class Settings(BaseSettings):
    """Настройки бота."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    API_OPENWEATHERMAP: str  # API для сайта https://api.openweathermap.org
    TOKEN: str
    BOT_COMMAND: List[BotCommand] = [
        BotCommand(
            command="/start",
            description="Вызов меню бота",
        )
    ]  # Список коммнад для бота
    ULR_GEOLOCATED_OPENWEATHERMAP: str = "http://api.openweathermap.org/geo/1.0/direct?q={}&limit=5&appid={}"  # URL для получения геолокации
    URL_CURRENT_OPENWEATHERMAP: str = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"  # URL для текущего прогноза погоды
    URL_FEATURE_OPENWEATHERMAP: str = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"  # URL для текущего прогноза погоды на 5 дней
    URL_WEATHER_MAPS: str = "https://tile.openweathermap.org/map/{}/0/0/0.png?appid={}"  # URL для получения карт погоды
    URL_AIR_POLLUTION: str = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}"  # URL для получения данных о загрязнении воздуха
    PATH_TO_WEATHER_TRANSLATION: str = "static\\files\\openweathermap\\weather_translations.json"  # Путь для файла с переводами описаний прогноза погоды на русский язык
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
    }
    AQI: Dict = {
        1: "Хороший",
        2: "Удовлетворительный",
        3: "Средний",
        4: "Плохой",
        5: "Очень плохой",
    }  # Словарь индексов качества воздуха

    modelimage: ImageGeneration = ImageGeneration()
    image_description: ImageDescription = ImageDescription()
    find_video: FindVideo = FindVideo()


settings = Settings()
