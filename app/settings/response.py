from typing import Optional, Any
from dataclasses import dataclass

from pydantic import BaseModel


class ResponseData(BaseModel):
    """Модель для работы с сайтами."""

    status: Optional[int] = None
    message: Optional[Any] = None
    error: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
