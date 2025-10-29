import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


from keyboards.inline_kb import (
    get_button_generate_image,
    get_button_model_video_generate_by_caila,
)
from keyboards.reply_kb import get_cancel_button
from functions import (
    get_and_save_image,
    get_url_video_generate_by_caila,
    get_url_video_generate_by_neuroimg,
)
from settings.config import settings
from extension import bot

router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Генерация Изображений")
async def generate_image(message: Message):
    """Возвращает пользвотателю клавиатуру с выбором сайтов генераторов изображений."""

    await message.answer(
        text="Выберите нужный генератор изображений",
        reply_markup=get_button_generate_image(),
    )


# Логика генерации изображения для сайт pollinations.ai
class GenerateImage(StatesGroup):
    """FSM для генерации изображений"""

    count = State()
    source = State()
    model = State()


@router.callback_query(F.data.startswith("generate_image "))
async def start_generate_image_pollinations(call: CallbackQuery, state: FSMContext):
    """Работа с FSM GenerateImage.Просит пользователя выбрать варианты моделей"""

    _, source = call.data.split(" ")

    await state.set_state(GenerateImage.source)
    await state.update_data(source=source)

    if source == "pollinations" or source == "neuroimg":
        await add_model_generate_image(call=call, state=state)
    else:
        data = await state.get_state()
        await bot.send_message(
            chat_id=call.message.chat.id,
            text="Доступные варианты",
            reply_markup=get_cancel_button(),
        )
        await call.message.answer(
            text="Выберите модель из списка вариантов",
            reply_markup=get_button_model_video_generate_by_caila(),
        )

    # await state.set_state(GenerateImagePollinations.image)


@router.message(GenerateImage.source, F.text == "Отмена")
@router.message(GenerateImage.model, F.text == "Отмена")
async def cancel_generate_image_pollinations(message: Message, state: FSMContext):
    """Работа с FSM GenerateImagePollinations. Отменяет все действия."""

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()
    await message.answer(
        text="Генерация изображеня отменена",
        reply_markup=ReplyKeyboardRemove(),
    )
    await generate_image(message=message)


@router.callback_query(GenerateImage.source, F.data.startswith("gv "))
async def add_model_generate_image(call: CallbackQuery, state: FSMContext):
    _, model = call.data.split(" ")

    await state.set_state(GenerateImage.count)
    await state.update_data(count=0)
    await state.set_state(GenerateImage.model)
    await state.update_data(model=model)
    await call.message.answer(
        text="Введите описание для генерируемого изображения",
        reply_markup=get_cancel_button(),
    )


@router.message(GenerateImage.model, F.text)
async def finish_generate_image(message: Message, state: FSMContext):
    """Работа с FSM GenerateImagePollinations. Возвращает пользователю сгенерированную картинку."""

    data = await state.get_data()
    source = data["source"]
    model = data.get("model")

    # Защита от спама когда пользователь делает много запросов
    count = data["count"]
    if count == 1:
        return
    else:
        await state.set_state(GenerateImage.count)
        await state.update_data(count=1)
        await state.set_state(GenerateImage.model)

        await bot.send_message(
            chat_id=message.chat.id, text="Идет генерация изображения"
        )

        if source == "pollinations":
            url = settings.modelimage.pollinations.IMAGE_GENERATE.format(message.text)
            path_image = get_and_save_image(url=url, filename="pollinations.jpg")
        elif source == "neuroimg":
            url = get_url_video_generate_by_neuroimg(
                url=settings.modelimage.neuroimg.URL_IMAGE_GENERATE,
                api_key=settings.modelimage.neuroimg.ApiKey,
                prompt=message.text,
            )
            if not url:
                await state.clear()
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Произошла ошибка при доступе к сайту, попробуйте позже...",
                    reply_markup=ReplyKeyboardRemove()
                )
                await generate_image(message=message)
                return
            else:
                path_image = get_and_save_image(url=url, filename="neuroimg.jpg")

        elif source == "caila":
            url = get_url_video_generate_by_caila(
                url=settings.modelimage.caila.URL_IMAGE_GENERATE,
                api_key=settings.modelimage.caila.ApiKey,
                model=model,
                promtp=message.text.strip(),
            )

            if url == 400:
                await state.clear()
                await message.answer(
                    "Введено неккоректное описание изображения.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                await generate_image(message=message)
                return
            gpt_image_1 = True if model == "gpt-image-1" else None
            path_image = get_and_save_image(
                url=url,
                filename="caila.jpg",
                gpt_image_1=gpt_image_1,
            )
        elif not source:
            await message.answer("Выберите модель из списка вариантов")

        if path_image:
            await state.clear()
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=FSInputFile(path=path_image),
                reply_markup=ReplyKeyboardRemove(),
            )
            os.remove(path=path_image)
            await generate_image(message=message)
        else:
            await state.clear()
            await message.answer(
                "Произошла ошибка при генерации изображения, попробуйте позже",
                reply_markup=ReplyKeyboardRemove(),
            )
            await generate_image(message=message)
