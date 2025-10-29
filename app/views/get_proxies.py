from aiogram.filters import StateFilter
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from settings.config import settings
from keyboards.inline_kb import get_button_proxies
from keyboards.reply_kb import get_start_button_bot
from bot_functions.get_proxies import get_proxies_by_webshare
from extension import bot
from settings.response import ResponseData


router: Router = Router(name=__name__)


class Proxies(StatesGroup):
    """FSM для работы получения прокси."""

    spam: State = State()


@router.message(StateFilter(None), F.text == "Получить список прокси")
async def get_proxies_list(message: Message):
    """Возвращает пользователю кнопки выбора из списка достуных источников прокси."""

    await message.answer(
        text="Доступные варианты",
        reply_markup=get_button_proxies(),
    )


@router.message(Proxies.spam, F.text)
async def get_message_proxies(message: Message, state: FSMContext):
    """
    Раблота с FSM Proxies.Отправляем пользователю сообщение если произошел
    ввод текста при обработке запроса
    """
    await message.reply("Идет обработка запроса, пожалуйста подождите...")


@router.callback_query(F.data.startswith("proxies "))
async def add_source_proxies(call: CallbackQuery, state: FSMContext):
    """Возвращает пользователю список прокси."""
    _, source = call.data.split(" ")

    await call.message.edit_reply_markup(reply_markup=None)

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="Идет обработка запроса.Ждите...",
        reply_markup=ReplyKeyboardRemove(),
    )
    # Встаем в состояние spam для отправки пользователю сообщения при запросе
    await state.set_state(Proxies.spam)

    if source == "webshare":
        data: ResponseData = await get_proxies_by_webshare(
            url_config=settings.proxies.webshare.URL_CONFIG,
            api_key=settings.proxies.webshare.ApiKey,
            url_proxeis_list=settings.proxies.webshare.URL_PROXIES_LIST,
        )
        if data.message:
            await state.clear()
            await call.message.answer(text=data.message)
            await bot.send_message(
                chat_id=call.message.chat.id,
                text="Главное меню бота",
                reply_markup=get_start_button_bot(),
            )
        else:
            await state.clear()
            await call.message.answer(data.error)
            await bot.send_message(
                chat_id=call.message.chat.id,
                text="Главное меню бота",
                reply_markup=get_start_button_bot(),
            )
