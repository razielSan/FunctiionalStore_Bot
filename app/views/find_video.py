import time

from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from keyboards.inline_kb import (
    get_button_find_video,
    get_button_choice_sorted_youtube_video,
)
from keyboards.reply_kb import get_cancel_button
from keyboards.inline_kb import get_button_find_video_youtube_by_forward_or_back
from functions import get_description_video_by_youtube
from extension import bot


router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Поиск Видео")
async def find_video(message: Message):
    """Возвращает клавиатуры с выбором источников поиска видео."""
    await message.answer(
        text="Доступные варианты",
        reply_markup=get_button_find_video(),
    )


class FindVideo(StatesGroup):
    """FSM для поиска видео."""

    spam_counter = State()
    source = State()
    sort = State()
    video_search_list = State()
    end_search_video = State()


@router.callback_query(F.data.startswith("FindVideo "))
async def start_find_video(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindVideo.Сохраняет источник для поиска видео.Просит у пользователя
    ввести название видео.
    """

    _, source = call.data.split(" ")
    await state.set_state(FindVideo.source)
    await state.update_data(source=source)

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
    await find_video(message=message)


@router.callback_query(FindVideo.sort, F.data.startswith("sort "))
async def add_sorted_by_find_video(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindVideo.Просит у пользователя ввести название видео для поиска."""
    _, sort = call.data.split(" ")
    await state.update_data(sort=sort)

    await call.message.answer(text="Введите название видео")
    await state.set_state(FindVideo.spam_counter)
    await state.update_data(spam_counter=0)
    await state.set_state(FindVideo.video_search_list)


@router.message(FindVideo.video_search_list, F.text)
async def finish_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Выводит пользователю список из названий, ссылок найденных видео."""

    data = await state.get_data()
    source = data["source"]
    sort = data["sort"]
    spam_counter = data["spam_counter"]

    # Защита от спама когда пользователь делает много запросов
    if spam_counter == 1:
        return
    else:
        await state.set_state(FindVideo.spam_counter)
        await state.update_data(spam_counter=0)
        await state.set_state(FindVideo.video_search_list)

        if source == "youtube":
            result = get_description_video_by_youtube(
                name_video=message.text,
                sort=sort,
            )
            await state.update_data(video_search_list=result)

            await bot.send_message(
                chat_id=message.chat.id,
                text="Нажмите 'Завершить' чтобы закончить поиск видео",
                reply_markup=ReplyKeyboardRemove(),
            )

            await message.answer(
                text=result[0],
                reply_markup=get_button_find_video_youtube_by_forward_or_back(
                    video_search_list=result,
                ),
            )
            await state.set_state(FindVideo.end_search_video)


@router.message(FindVideo.end_search_video, F.text)
async def message_user(message: Message):
    """Отправляет пользователю сообщение чтобы он узнал если он не знает как
    закончить поиск видео
    """
    await bot.send_message(
        chat_id=message.chat.id,
        text="Нажмите 'Завершить' чтобы закончить поиск видео",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.callback_query(FindVideo.end_search_video, F.data == "end_search_video")
@router.callback_query(FindVideo.end_search_video, F.data.startswith("fvy "))
async def finish_find_video(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindVideo.Пролистывает найденные виедо или завершает работу поиска видео."""

    data = call.data

    if data == "end_search_video":
        await state.clear()
        await call.message.answer(
            "Поиск Видео Закончен", reply_markup=ReplyKeyboardRemove()
        )
        await find_video(message=call.message)
    else:
        _, _, count = data.split(" ")
        data = await state.get_data()
        video_search_list = data["video_search_list"]

        await bot.edit_message_text(
            text=video_search_list[int(count)],
            reply_markup=get_button_find_video_youtube_by_forward_or_back(
                video_search_list=video_search_list,
                count=int(count),
            ),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
