from typing import Dict, List

from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from keyboards.inline_kb import (
    get_button_find_video,
    get_button_choice_sorted_youtube_video,
)
from keyboards.reply_kb import get_cancel_button, get_start_button_bot
from keyboards.inline_kb import get_button_for_forward_or_back
from bot_functions.find_video import get_description_video_by_youtube
from extension import bot
from settings.config import settings
from settings.response import ResponseData


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Поиск Видео")
async def find_video(message: Message):
    """Возвращает клавиатуры с выбором источников поиска видео."""
    await message.answer(
        text="Доступные варианты",
        reply_markup=get_button_find_video(),
    )


class FindVideo(StatesGroup):
    """FSM для поиска видео."""

    spam: State = State()
    source: State = State()
    sort: State = State()
    video_search_list: State = State()
    end_search_video: State = State()


@router.callback_query(F.data.startswith("FindVideo "))
async def start_find_video(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindVideo.Сохраняет источник для поиска видео.Просит у 
       пользователя ввести название видео.
    """

    _, source = call.data.split(" ")
    await state.set_state(FindVideo.source)
    await state.update_data(source=source)

    await call.message.edit_reply_markup(reply_markup=None)

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="Поиск по youtube",
        reply_markup=get_cancel_button(),
    )
    await call.message.answer(
        text="Выберите вариант поиска",
        reply_markup=get_button_choice_sorted_youtube_video(),
    )
    await state.set_state(FindVideo.sort)


@router.message(FindVideo.end_search_video, F.text == "Отмена")
@router.message(FindVideo.video_search_list, F.text == "Отмена")
@router.message(FindVideo.sort, F.text == "Отмена")
@router.message(FindVideo.source, F.text == "Отмена")
async def cancel_find_video(message: Message, state: FSMContext):
    """Раблота с FSM FindVideo.Отменяет все действия."""

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Поиск видео отменен",
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(FindVideo.spam, F.text)
async def get_message_find_video(message: Message, state: FSMContext):
    """
    Раблота с FSM FindVideo.Отправляет пользователю сообщение
    если он что то написал при обработке запроса.
    """
    await message.reply("Идет обработка запроса, пожалуйста подождите...")


@router.callback_query(FindVideo.sort, F.data.startswith("sort "))
async def add_sorted_by_find_video(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindVideo.Просит у пользователя ввести название видео для поиска."""
    _, sort = call.data.split(" ")
    await state.update_data(sort=sort)

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(text="Введите название видео")
    await state.set_state(FindVideo.video_search_list)


@router.message(FindVideo.video_search_list, F.text)
async def finish_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Выводит пользователю список из названий, ссылок найденных видео."""

    data = await state.get_data()
    source = data["source"]
    sort = data["sort"]

    # Встаем в состояние spam для отправки пользователю сообщений во время 
    # обработки запроса
    await state.set_state(FindVideo.spam)

    if source == "youtube":

        await message.answer(
            "Идет поиск.Ожидайте....",
            reply_markup=ReplyKeyboardRemove(),
        )

        # Отправляем запрос на ютуб для поиска видео
        response_youtube: ResponseData = await get_description_video_by_youtube(
            name_video=message.text,
            sort=sort,
            api_key=settings.find_video.youtube.YoutubeApiKey,
            youtube_video_url=settings.find_video.youtube.VIDEO_URL,
            youtube_channel_url=settings.find_video.youtube.CHANNEL_URL,
        )

        if response_youtube.message:
            
            # Обновляем FSM FindVideo.Добавляем список с описаниями видео
            await state.update_data(video_search_list=response_youtube.message)

            await bot.send_message(
                chat_id=message.chat.id,
                text="Нажмите 'Отмена' чтобы закончить поиск видео",
                reply_markup=get_cancel_button(),
            )

            await message.answer(
                text=response_youtube.message[0],
                reply_markup=get_button_for_forward_or_back(
                    video_search_list=response_youtube.message,
                ),
            )
            await state.set_state(FindVideo.end_search_video)
        else:
            await message.answer(
                text=f"{response_youtube.error}\n\nВведите, "
                "снова, название видео для поиска",
                reply_markup=get_cancel_button(),
            )
            await state.set_state(FindVideo.video_search_list)


@router.message(FindVideo.end_search_video, F.text)
async def message_user(message: Message):
    """
    Работа с FSM FindVideo.Отправляет пользователю сообщение при состоянии
    end_search_video когда пользователь вводит текст
    """
    await bot.send_message(
        chat_id=message.chat.id,
        text="Нажмите 'Отмена' чтобы закончить поиск видео",
    )


@router.callback_query(FindVideo.end_search_video, F.data.startswith("fb "))
async def finish_find_video(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindVideo.Пролистывает найденные виедо или завершает работу поиска видео."""

    _, _, count = call.data.split(" ")
    data: Dict = await state.get_data()
    video_search_list: List = data["video_search_list"]

    await bot.edit_message_text(
        text=video_search_list[int(count)],
        reply_markup=get_button_for_forward_or_back(
            video_search_list=video_search_list,
            count=int(count),
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
