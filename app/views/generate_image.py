import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import get_button_generate_image
from keyboards.reply_kb import get_cancel_button
from functions import get_and_save_image
from config import settings
from extension import bot

router = Router(name=__name__)


@router.message(F.text == "Генерация Изображений")
async def generate_image(message: Message):
    """Возвращает пользвотателю клавиатуру с выбором сайтов генераторов изображений."""

    await message.answer(
        text="Выберите нужный генератор изображений",
        reply_markup=get_button_generate_image(),
    )


# Логика генерации изображения для сайт pollinations.ai
class GenerateImagePollinations(StatesGroup):
    """FSM для генерации изображений c сайта pollinations.api."""
    image = State()


@router.callback_query(F.data == "pollinations")
async def start_generate_image_pollinations(call: CallbackQuery, state: FSMContext):
    """Работа с FSM GenerateImagePollinations.Просит пользователя ввести описание для изображения."""

    await call.message.answer(
        text="Введите описание для генерируемого изображения",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(GenerateImagePollinations.image)


@router.message(GenerateImagePollinations.image, F.text == "Отмена")
async def cancel_generate_image_pollinations(message: Message, state: FSMContext):
    """Работа с FSM GenerateImagePollinations. Отменяет все действия."""

    current_state = await state.get_state()

    if current_state is None:
        return

    await message.answer(
        text="Генерация картинки c помощью pollinations.ai отменена",
        reply_markup=ReplyKeyboardRemove(),
    )
    await generate_image(message=message)
    await state.clear()


@router.message(GenerateImagePollinations.image, F.text)
async def finish_generate_image_pollinations(message: Message, state: FSMContext):
    """Работа с FSM GenerateImagePollinations. Возвращает пользователю сгенерированную картинку."""

    await bot.send_message(chat_id=message.chat.id, text="Идет генерация изображения")

    url = settings.modelimage.pollinations.IMAGE_GENERATE.format(message.text)

    path_image = get_and_save_image(url=url, filename="pollinations.jpg")

    if path_image:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=FSInputFile(path=path_image),
            reply_markup=ReplyKeyboardRemove(),
        )
        os.remove(path=path_image)
        await state.clear()
        await generate_image(message=message)
    else:
        await message.answer(
            "Произошла ошибка при скачивании, попробуйте позже",
            reply_markup=ReplyKeyboardRemove(),
        )
        await generate_image(message=message)
