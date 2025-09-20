import os
from pathlib import Path
from typing import Dict, List
from random import shuffle

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from keyboards.inline_kb import (
    get_button_recommender_system,
    get_button_recommender_system_by_kinopoisk,
)
from keyboards.reply_kb import get_cancel_button
from keyboards.inline_kb import get_button_for_forward_or_back
from functions import (
    searches_for_videos_by_name_for_kinopoisk,
    get_recommender_video_for_kinopoisk,
    get_description_video_from_kinopoisk,
)
from extension import bot


router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Рекомендательная система")
async def main(message: Message):
    """Главная функция рекомендательной системы."""
    await message.answer(
        text="Доступные варианты",
        reply_markup=get_button_recommender_system(),
    )


@router.callback_query(F.data.startswith("recsystem "))
async def get_button_choice_recommender_system(call: CallbackQuery):
    """Возвращает инлайн клавитуры с вариантами выбора для рекомендательных систем."""
    _, source = call.data.split(" ")

    if source == "kinopoisk":
        await call.message.answer(
            text="Доступные варианты",
            reply_markup=get_button_recommender_system_by_kinopoisk(),
        )


class RecomenderSystemFSM(StatesGroup):
    """Модель FSM для рекомендательно системы."""

    kinopoisk = State()
    kinopoisk_recommender_list = State()


@router.callback_query(F.data.startswith("kinopoisk_recommender "))
async def add_kinopoisk(call: CallbackQuery, state: FSMContext):
    """Работа с FSM RecomenderSystemFSM.Просит у пользователя ввести
    необходимые данные для рекомендации.
    """

    _, recommender = call.data.split(" ")
    await state.set_state(RecomenderSystemFSM.kinopoisk)
    await state.update_data(kinopoisk=recommender)

    if recommender == "name":
        await call.message.answer(
            "Введите название фильма, для которого хотите найти похожие фильмы",
            reply_markup=get_cancel_button(),
        )


@router.message(RecomenderSystemFSM.kinopoisk, F.text == "Отмена")
@router.message(RecomenderSystemFSM.kinopoisk_recommender_list, F.text == "Отмена")
async def cancel_find_video(message: Message, state: FSMContext):
    """Раблота с FSM RecomenderSystemFSM.Отменяет все действия."""

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Рекомендательная система отменена",
        reply_markup=ReplyKeyboardRemove(),
    )
    await main(message=message)


@router.message(RecomenderSystemFSM.kinopoisk_recommender_list, F.text)
async def message_user(message: Message):
    """Отправляет пользователю сообщение чтобы он узнал если он не знает как
    закончить рекомендательную систем
    """
    await bot.send_message(
        chat_id=message.chat.id,
        text="Нажмите 'Отмена' чтобы закончить поиск по рекомендации",
    )


@router.message(RecomenderSystemFSM.kinopoisk, F.text)
async def get_data_recominder(message: Message, state: FSMContext):
    """Работа с FSM RecomenderSystemFSM. Возвращает рекомендации для https://www.kinopoisk.ru/."""

    data = await state.get_data()
    kinopoisk = data["kinopoisk"]

    if kinopoisk == "name":
        await message.answer("Идет составление рекомендации.Ожидайте...")
        name = searches_for_videos_by_name_for_kinopoisk(name=message.text)
        if name.get("docs", 0):
            json_kinopoisk: Dict = name.get("docs")[0]

            # Делает два запроса с разными рейтингами
            recommender_video_list_1: List = get_recommender_video_for_kinopoisk(
                list_genres=json_kinopoisk.get("genres"),
                limit=25,
                type_video=json_kinopoisk.get("type"),
                rating="1-5",
            )

            recommender_video_list_2: List = get_recommender_video_for_kinopoisk(
                list_genres=json_kinopoisk.get("genres"),
                limit=50,
                type_video=json_kinopoisk.get("type"),
                rating="6-10",
            )

            # Состваляет общий рекомендательный список
            recommender_video_list = []
            recommender_video_list.extend(recommender_video_list_1)
            recommender_video_list.extend(recommender_video_list_2)

            shuffle(recommender_video_list)

            data: str = get_description_video_from_kinopoisk(
                data=recommender_video_list[0],
            )

            poster = recommender_video_list[0].get("poster", 0)

            # Проверяет есть ли фотография в данных
            photo = ""
            if poster:
                photo = recommender_video_list[0]["poster"].get("url", 0)

            await state.set_state(RecomenderSystemFSM.kinopoisk_recommender_list)
            await state.update_data(kinopoisk_recommender_list=recommender_video_list)

            if photo:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=data,
                    reply_markup=get_button_for_forward_or_back(
                        video_search_list=recommender_video_list,
                        count=0,
                        step=1,
                    ),
                )
            else:
                path: Path = Path(__file__).parent.parent
                photo: str = os.path.join(path, f"static/img/none.png")

                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=FSInputFile(path=photo),
                    caption=data,
                    reply_markup=get_button_for_forward_or_back(
                        video_search_list=recommender_video_list,
                        count=0,
                        step=1,
                    ),
                )
        else:
            await message.answer(
                "Данный фильм не был найден\n\n"
                "Введите название фильма, для которого хотите найти похожие фильмы"
            )


@router.callback_query(
    RecomenderSystemFSM.kinopoisk_recommender_list, F.data.startswith("fb ")
)
async def scrolls_through_the_list_of_recommendations(
    call: CallbackQuery,
    state: FSMContext,
):
    """Работа с FSM RecomenderSystemFSM.Пролистывает видео рекомендательной системы."""
    _, _, count = call.data.split(" ")
    data = await state.get_data()
    recommender_list = data["kinopoisk_recommender_list"]

    description = get_description_video_from_kinopoisk(
        data=recommender_list[int(count)],
    )

    poster = recommender_list[int(count)].get("poster", 0)

    photo = ""
    if poster:
        photo = recommender_list[int(count)]["poster"].get("url", 0)

    if photo:
        try:

            await bot.edit_message_media(
                media=InputMediaPhoto(media=photo, caption=description),
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                reply_markup=get_button_for_forward_or_back(
                    video_search_list=recommender_list,
                    count=int(count),
                ),
            )
        except Exception as err:
            path: Path = Path(__file__).parent.parent
            photo: str = os.path.join(path, f"static/img/none.png")

            await bot.edit_message_media(
                media=InputMediaPhoto(media=FSInputFile(photo), caption=description),
                message_id=call.message.message_id,
                chat_id=call.message.chat.id,
                reply_markup=get_button_for_forward_or_back(
                    video_search_list=recommender_list,
                    count=int(count),
                ),
            )

    else:
        path: Path = Path(__file__).parent.parent
        photo: str = os.path.join(path, f"static/img/none.png")

        await bot.edit_message_media(
            media=InputMediaPhoto(media=FSInputFile(path=photo), caption=description),
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            reply_markup=get_button_for_forward_or_back(
                video_search_list=recommender_list,
                count=int(count),
            ),
        )
