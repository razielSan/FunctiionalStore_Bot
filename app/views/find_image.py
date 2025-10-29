from pathlib import Path
from typing import Dict
from typing import List
import uuid

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

from extension import bot
from errors_handlers.main import chek_number_is_positivity
from bot_functions.find_image import (
    find_image_with_goole_and_save_image,
    get_url_link_posters_for_kinopoisk,
)
from bot_functions.total import (
    get_list_images_name,
    delete_images_and_archive,
    save_images_with_zip_archive,
    save_images,
)
from settings.config import settings
from keyboards.reply_kb import get_cancel_button, get_start_button_bot
from keyboards.inline_kb import get_button_for_find_image
from settings.response import ResponseData


router: Router = Router(name=__name__)


# Логика для поиска изображений
class FindImage(StatesGroup):
    """FSM для поиска изображений."""

    spam: State = State()
    name: State = State()
    poster: State = State()
    count: State = State()


@router.message(StateFilter(None), F.text == "Поиск Изображений")
async def handler_find_image(message: Message):
    """Отправляет пользователю клавиатуру с выринтами выбора поиска изображений."""

    await message.answer(
        text="Варианты выбора",
        reply_markup=get_button_for_find_image(),
    )


@router.callback_query(F.data.startswith("find_image "))
async def start_find_image(call: CallbackQuery, state: FSMContext):
    """Работа с FSM FindImage.Просит у пользователя ввести название изображения"""
    _, data = call.data.split(" ")

    await call.message.edit_reply_markup(reply_markup=None)
    if data == "name":
        await call.message.answer(
            "Введите название изображение которое хотите найти",
            reply_markup=get_cancel_button(),
        )
    elif data == "poster":
        await state.set_state(FindImage.poster)
        await state.update_data(poster=True)
        await call.message.answer(
            "Введите названия фильмов для скачивания обложек через точку в "
            "формате\n\nматрица.криминальное чтиво.пражский студент",
            reply_markup=get_cancel_button(),
        )
    await state.set_state(FindImage.name)


@router.message(FindImage.name, F.text == "Отмена")
@router.message(FindImage.count, F.text == "Отмена")
async def cancel_find_image_handler(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Отменяет все действия."""
    await state.clear()
    await message.answer(text="Поиск изображений отменен....")
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(FindImage.spam, F.text)
async def get_message_for_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Отправляет пользователю сообщение при обработке информации."""
    await message.reply("Идет обработка запроса, пожалуйста подождите...")


@router.message(FindImage.name, F.text)
async def add_name_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Добавляет имя FSM FindImage и просит у пользователя
    ввести количество изображений для поиска."""

    data: Dict = await state.get_data()

    await state.update_data(name=message.text)
    if data.get("poster", None):
        await finish_find_image(message=message, state=state)
        return
    else:
        await message.answer(
            "Введите необходимое количество изображений для скачивания"
        )
    await state.set_state(FindImage.count)


@router.message(FindImage.count, F.text)
async def finish_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Скидывает zip архив пользователю найденных изображений."""

    await state.set_state(FindImage.spam)

    data: Dict = await state.get_data()

    if data.get("poster", None):

        # Создаем список с названиями фильмов
        list_title_films: List = data.get("name").split(".")
        list_url_films: List = []
        for title in list_title_films:
            list_url_films.append(
                settings.recommender_system.kinopoisk.URL_SEARCH_VIDEO_NAME.format(
                    1, title
                )
            )

        await message.answer(
            f"🔍 Ищу обложки по запросу: {data.get('name')}...",
            reply_markup=ReplyKeyboardRemove(),
        )

        path_folder = settings.find_image.PATH_FIND_IMAGE / str(message.from_user.id)

        # Путь до архива с картинками
        path_archive = path_folder / f"{uuid.uuid4().hex}.zip"

        # Формируем заголовок запроса
        HEADERS: Dict = settings.recommender_system.kinopoisk.HEADERS.copy()
        HEADERS["X-API-KEY"] = settings.recommender_system.kinopoisk.ApiKey
        data: ResponseData = await get_url_link_posters_for_kinopoisk(
            list_url=list_url_films,
            headers=HEADERS,
            message=message,
        )

        if data.message:

            # Сохраняем картинки и получаем список с путями до картинок
            data: ResponseData = await save_images(
                list_url=data.message,
                path=path_folder,
                message=message,
            )

            if data.message:
                # Сохраняем изображения в архив

                await message.answer(text="Идет упаковка в архив")

                save_images_with_zip_archive(
                    path_folder=path_folder,
                    path_archive=path_archive,
                    list_images_name=data.message,
                )

                await bot.send_document(
                    chat_id=message.chat.id,
                    document=FSInputFile(path=str(path_archive)),
                    caption="Скаченные изображения",
                )
                # Удаляем изображения и архив
                delete_images_and_archive(
                    path_folder=path_folder,
                )
                await state.clear()
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Главное меню бота",
                    reply_markup=get_start_button_bot(),
                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"{data.error}\n\nВведите, снова, названия фильмов для скачивания "
                    "обложек через точку в формате\n\nматрица.криминальное чтиво.пражский студент",
                    reply_markup=get_cancel_button(),
                )
                await state.set_state(FindImage.name)
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"{data.error}\n\nВведите, снова, названия фильмов для скачивания "
                "обложек через точку в формате\n\nматрица.криминальное чтиво.пражский студент",
                reply_markup=get_cancel_button(),
            )
            await state.set_state(FindImage.name)
    else:
        number: ResponseData = chek_number_is_positivity(number=message.text)

        # Проверяем ввел ли пользователь число

        if number.error:
            await message.answer(
                text=f"{number.error}\n\n"
                "Введите снова необходимое количество изображений для скачивания",
                reply_markup=get_cancel_button(),
            )
            await state.set_state(FindImage.count)
        else:
            data = await state.get_data()
            name: str = data["name"]
            await message.answer(
                f"🔍 Ищу изображения по запросу: {name}...",
                reply_markup=ReplyKeyboardRemove(),
            )
            path_image: Path = settings.find_image.PATH_FIND_IMAGE / str(
                message.from_user.id
            )

            # Путь до архива с картинками
            path_archive: Path = path_image / f"{name}.zip"

            filters: Dict = {"size": "large"}
            data: ResponseData = await find_image_with_goole_and_save_image(
                name=name,
                count=number.message,
                filters=filters,
                path=path_image,
                message=message,
            )

            if data.message:

                # Указываем имена изображений
                list_images_name: List = get_list_images_name(
                    count_images=data.message,
                    path_find_image=path_image,
                )
                # Сохраняем изображения в архив

                await message.answer(text="Идет упаковка в архив")

                save_images_with_zip_archive(
                    path_folder=path_image,
                    path_archive=path_archive,
                    list_images_name=list_images_name,
                )

                await bot.send_document(
                    chat_id=message.chat.id,
                    document=FSInputFile(path=str(path_archive)),
                    caption="Скаченные изображения",
                    reply_markup=ReplyKeyboardRemove(),
                )

                # Удаляем изображения и архив
                delete_images_and_archive(
                    path_folder=path_image,
                )

                await state.clear()
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Главное меню бота",
                    reply_markup=get_start_button_bot(),
                )

            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"{data.error}\n\nВведите, cнова, название изображения "
                    "которое хотите найти ",
                    reply_markup=get_cancel_button(),
                )
                await state.set_state(FindImage.name)
