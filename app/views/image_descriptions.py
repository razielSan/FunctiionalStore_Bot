import os
from pathlib import Path

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline_kb import get_button_image_description
from keyboards.reply_kb import get_cancel_button
from functions import get_image_description_by_immaga
from extension import bot


router = Router(name=__name__)


@router.message(F.text == "Описание Изображений")
async def image_description(message: Message):
    await message.answer(
        text="Достуные варианты",
        reply_markup=get_button_image_description(),
    )


# Логика для описание изоабражений с сайта
class ImageDescription(StatesGroup):
    """FSM для описание изображений"""

    image_name = State()


@router.callback_query(F.data == "immaga")
async def start_image_description_imagga(call: CallbackQuery, state: FSMContext):
    """Работса с FSM ImageDescription.Просит у польователя скинуть фотографию."""

    await call.message.answer(
        text="Скидывайте фотографию для анализа изображения",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(ImageDescription.image_name)


@router.message(ImageDescription.image_name, F.text == "Отмена")
async def cancel_image_description_imagg(message: Message, state: FSMContext):
    """Работа с FSM ImageDescription.Отменяет все действия."""

    current_state = await state.get_state()

    if current_state is None:
        return

    await message.answer(
        "Описание изображений отменено",
        reply_markup=ReplyKeyboardRemove(),
    )

    await image_description(message=message)
    await state.clear()


@router.message(ImageDescription.image_name)
async def finish_image_description_imagga(message: Message, state: FSMContext):
    """Работа с FSM ImageDescription.Отправляет пользователю описание изображения"""

    if message.content_type == ContentType.PHOTO:
        await message.answer("Идет анализ изображения")
        await bot.download(file=message.photo[-1].file_id, destination="immaga.jpg")
        result, mess = get_image_description_by_immaga(language="ru", limit=20)
        if result:
            await bot.send_message(chat_id=message.chat.id, text=result)
            await image_description(message=message)
            await state.clear()
            os.remove(os.path.join(Path(__file__).parent.parent, "immaga.jpg"))
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"{mess['err']}\n\nСкидывайте снова фотографию для анализа изображения",
            )
            os.remove(os.path.join(Path(__file__).parent.parent, "immaga.jpg"))
    else:
        await message.answer(
            "Скидываемое изображение должно быть формата jpg, jpeg, png или gif\n\n"
            "Скидывайте снова фотографию для анализа изображения"
        )
