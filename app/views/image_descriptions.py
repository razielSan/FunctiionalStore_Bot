import os
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline_kb import get_button_image_description
from keyboards.reply_kb import get_cancel_button, get_start_button_bot
from bot_functions.image_descriptions import get_image_description_by_immaga
from extension import bot
from settings.config import settings
from settings.response import ResponseData


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Описание Изображений")
async def image_description(message: Message):
    await message.answer(
        text="Достуные варианты",
        reply_markup=get_button_image_description(),
    )


# Логика для описание изоабражений с сайта
class ImageDescription(StatesGroup):
    """FSM для описание изображений."""

    spam: State = State()
    image_name: State = State()


@router.callback_query(F.data == "immaga")
async def start_image_description_imagga(call: CallbackQuery, state: FSMContext):
    """Работса с FSM ImageDescription.Просит у пользователя скинуть фотографию."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text="Скидывайте фотографию для анализа изображения",
        reply_markup=get_cancel_button(),
    )

    await state.set_state(ImageDescription.image_name)


@router.message(ImageDescription.image_name, F.text == "Отмена")
async def cancel_image_descripton_handler(message: Message, state: FSMContext):
    """Работа с FSM ImageDescription.Оменяет все действия."""

    await state.clear()
    await message.answer(
        text="Анализ изображений отменен",
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(ImageDescription.spam, F.text)
async def get_message_for_image_description(message: Message, state: FSMContext):
    """Работа с FSM ImageDescription.Отправляет пользователю сообщение если он пишет
    во время обработки запроса.
    """
    await message.reply("Идет обработка запроса, пожалуйста подождите...")


@router.message(ImageDescription.image_name)
async def finish_image_description_imagga(message: Message, state: FSMContext):
    """Работа с FSM ImageDescription.Отправляет пользователю описание изображения."""

    await state.set_state(ImageDescription.spam)

    if message.content_type == ContentType.PHOTO:
        await message.answer(
            "Идет анализ изображения.....",
            reply_markup=ReplyKeyboardRemove(),
        )
        path_img: Path = (
            settings.image_description.PATH_TO_IMAGE_DESCRIPTON / "immaga.jpg"
        )
        await bot.download(
            file=message.photo[-1].file_id,
            destination=path_img,
        )
        data_image: ResponseData = await get_image_description_by_immaga(
            path_img=path_img,
            language="ru",
            limit=20,
            key_autorization=settings.image_description.immaga.AUTHORIZATION,
            url_tags=settings.image_description.immaga.URL_TAGS,
            upload_endpoint=settings.image_description.immaga.UPLOAD_ENDPOINT,
        )

        if data_image.message:
            await state.clear()
            await bot.send_message(
                chat_id=message.chat.id,
                text=data_image.message,
                reply_markup=ReplyKeyboardRemove(),
            )
            if os.path.exists(path_img):
                os.remove(path_img)
            await bot.send_message(
                chat_id=message.chat.id,
                text="Главное меню бота",
                reply_markup=get_start_button_bot(),
            )

        else:
            await message.answer(
                text=f"{data_image.error}\n\nСкидывайте,снова, фотографию для "
                "анализа изображения",
                reply_markup=get_cancel_button(),
            )
            if os.path.exists(path_img):
                os.remove(path_img)
            await state.set_state(ImageDescription.image_name)
    else:
        await state.set_state(ImageDescription.image_name)

        await message.answer(
            "Скидываемое изображение должно быть формата jpg, jpeg, png или gif\n\n"
            "Скидывайте снова фотографию для анализа изображения",
            reply_markup=get_cancel_button(),
        )
