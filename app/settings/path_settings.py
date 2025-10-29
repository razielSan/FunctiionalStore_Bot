from pathlib import Path


from pydantic_settings import SettingsConfigDict
from pydantic import BaseModel


class BasePathSettings(BaseModel):
    """Настройка для путей приложения."""

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent
    APP_DIR: Path = ROOT_DIR / "app"


path_settings: BasePathSettings = BasePathSettings()
