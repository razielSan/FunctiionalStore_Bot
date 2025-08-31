import time

from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline_kb import (
    get_button_find_video,
    get_button_choice_sorted_youtube_video,
)
from keyboards.reply_kb import get_cancel_button
from functions import get_description_video_by_youtube
from extension import bot


router = Router(name=__name__)


@router.message(F.text == "Поиск Видео")
async def find_video(message: Message):
    """Возвращает клавиатуры с выбором источников поиска видео."""
    await message.answer(
        text="Доступные варианты",
        reply_markup=get_button_find_video(),
    )


class FindVideo(StatesGroup):
    """FSM для поиска видео."""

    source = State()
    sort = State()


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


@router.callback_query(FindVideo.sort, F.data)
async def add_sorted_by_find_video(call: CallbackQuery, state: FSMContext):
    _, sort = call.data.split(" ")
    await state.update_data(sort=sort)

    await call.message.answer(text="Введите название видео")


@router.message(FindVideo.sort, F.text)
async def finish_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Выводит пользователю список из названий, ссылок найденных видео."""

    data = await state.get_data()
    source = data["source"]
    sort = data["sort"]
    print(sort)

    if source == "youtube":
        result = get_description_video_by_youtube(
            name_video=message.text,
            sort=sort,
        )
        number = 0
        for data in result[0:60:10]:
            data = "\n".join(result[number : number + 10])
            await message.answer(
                text=data,
                reply_markup=ReplyKeyboardRemove(),
            )
            number += 10
            time.sleep(1)
        await state.clear()
        await find_video(message=message)
