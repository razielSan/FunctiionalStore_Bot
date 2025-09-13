from pydantic import BaseModel, field_validator
from pydantic.networks import IPvAnyAddress


def chek_number_is_positivity(number: str):
    """Проверяет является ли входящее значение положительным числом.
    Возвращает кортеж формата

    (<Число>, {'err': None}) - Проверка пройдена
    (None, {'err': <Сообщение об ошибки>}) - Проверка не пройдена

    Args:
        number (str): Даныые для проверки в формате str
    """

    try:
        number = int(number)
        if number <= 0:
            return None, {"err": "Число должно быть больше 0"}
        return number, {"err": None}
    except Exception:
        return None, {"err": "Данные должны быть целым числом"}


class Ip4Handler(BaseModel):
    """Класс для валидации ip4 адресса."""

    ip4: IPvAnyAddress


class Ipi6Handler(BaseModel):
    """Класс для валидации ip6 адресса."""

    ip6: IPvAnyAddress


