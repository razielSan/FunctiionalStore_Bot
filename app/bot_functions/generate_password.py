from typing import List, Union
import random

from settings.config import settings
from settings.response import ResponseData


async def get_generateing_simple_or_difficult_password(
    password_hard: str,
    step: str = 3,
) -> ResponseData:
    """

    Генерирует сложный или простой пароль

    Args:
        password_hard (str): Тип сложности пароля
        step (str, optional): Шаг пароля[По умолчанию 3]

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
    """

    array_generating_password: List = []

    def random_generate_value(
        generation_data: str,
        step: int = 3,
    ) -> str:
        """
        
        Формирует строку содержащую колиечство шагов(step) состоящую либо из букв 
        либи из цифр

        Args:
            generation_data (Union[str, List]): Данные из которых будет генерироваться выборка
            step (int): Количество шагов пароля

        Returns:
            str: Возвращает строки содержащую или буквы или фифры
        """

        # Т.к в generation data может быть список выбираем рандомное значение из списка
        # если не список а строка выбираем ее
        values: str = (
            random.choice(generation_data)
            if isinstance(generation_data, list)
            else generation_data
        )

        # Определяем рандомное значение флага, если True то берем рандомное значение из
        # деneration data и следущие за ним цифры с учетом шага, если Fals то берем
        # рандомное значение genaration data и умножаем на шаг
        current_flag: bool = random.choice([True, False])
        if current_flag:
            start: int = random.randrange(0, len(generation_data) - step + 1)

            values = values[start : start + step]

            # Если False то берем значение в обратном порядке
            current_flag = random.choice([True, False])
            if current_flag:
                values = values[::-1]

        else:
            values = random.choice(values) * step

        return values

    # Определяем сложноый или простой нужен пароль
    count: int = 7 if password_hard == settings.password_generation.difficult else 4

    for _ in range(1, 16):  # Определяем количество паролей
        password: str = ""

        for i in range(1, count):  # Определяем количество символов в пароле

            # Определяем что будет добавляться буквы или цифвры
            generation_data: Union[str, List] = (
                settings.password_generation.digit
                if i % 2 == 0
                else settings.password_generation.keyboard_layout_english
            )
            result_password: str = random_generate_value(
                generation_data=generation_data,
            )

            password += result_password

        array_generating_password.append(password)
    # Формируем строку с паролями
    passwords: str = "\n".join(array_generating_password)
    return ResponseData(
        message=passwords,
        status=200,
    )
