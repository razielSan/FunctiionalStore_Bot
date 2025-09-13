from aiogram.filters import StateFilter
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import settings
from keyboards.inline_kb import get_button_proxies
from functions import get_proxies_by_webshare


router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Получить список прокси")
async def get_proxies_list(message: Message):
    """Возвращает пользователю кнопки выбора из списка достуных источников прокси."""

    await message.answer(
        text="Доступные варианты",
        reply_markup=get_button_proxies(),
    )


@router.callback_query(F.data.startswith("proxies "))
async def add_source_proxies(call: CallbackQuery):
    """Возвращает пользователю список прокси."""
    _, source = call.data.split(" ")

    if source == "webshare":
        data = get_proxies_by_webshare(
            url_config=settings.proxies.webshare.URL_CONFIG,
            api_key=settings.proxies.webshare.ApiKey,
            url_proxeis_list=settings.proxies.webshare.URL_PROXIES_LIST,
            path_proxies=settings.proxies.webshare.PATH,
            filename="proxies_list.txt",
        )
        if data:
            await call.message.answer(text=data)
        else:
            await call.message.answer(
                "Произошла ошибка при доступе к серверу, попробуйте позже")
