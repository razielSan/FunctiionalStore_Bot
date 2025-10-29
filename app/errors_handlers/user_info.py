from pydantic import BaseModel
from pydantic.networks import IPvAnyAddress


class Ip4Handler(BaseModel):
    """Класс для валидации ip4 адресса."""

    ip4: IPvAnyAddress


class Ipi6Handler(BaseModel):
    """Класс для валидации ip6 адресса."""

    ip6: IPvAnyAddress
