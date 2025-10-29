from typing import Dict, Callable, Optional, List
import asyncio
import os
from asyncio import Future, AbstractEventLoop
import random

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import (
    get_buttons_for_generating_video,
    get_buttons_for_generating_video_for_vheer,
)
from keyboards.reply_kb import get_cancel_button
from settings.config import settings
from extension import bot
from functions import create_video_by_is_vheer
from utils.generate_video import make_update_progress, make_cancel_chek


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Генерация Видео")
async def main(message: Message):
    """Отправляет пользователю инлайн кнопки с вариантами выбора генератора изображений."""
    await message.answer(
        "Выберите варианты",
        reply_markup=get_buttons_for_generating_video(),
    )


class FSMGenerateVideo(StatesGroup):
    """FSM для генерации видео"""

    counter_progress: State = State()
    cancel: State = State()
    source: State = State()
    description: State = State()
    image: State = State()
    prompt: State = State()


@router.message(FSMGenerateVideo.image, F.text == "Отмена")
@router.message(FSMGenerateVideo.prompt, F.text == "Отмена")
@router.message(FSMGenerateVideo.counter_progress, F.text == "Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    """Работса с FSMGenerateVideo.Отменяет все действия."""

    data: Dict = await state.get_data()
    current_state: Optional[str] = await state.get_state()

    image: Optional[str] = data.get("image", None)
    if image:
        if os.path.exists(path=image):
            os.remove(path=image)

    if current_state == "FSMGenerateVideo:counter_progress":
        await state.set_state(FSMGenerateVideo.cancel)
        await state.update_data(cancel=True)
        return

    await state.clear()
    await message.answer(
        text="Генерация видео отменена",
        reply_markup=ReplyKeyboardRemove(),
    )
    await main(message=message)


@router.message(FSMGenerateVideo.counter_progress, F.text)
async def get_message(message: Message, state: FSMContext):
    """Работа с FSMGenerateVideo.Отправляет пользователю сообщение если он
    совершил какое либо действие при статусе counter_progress.
    """

    await message.reply("Подождите процесса загрузки видео или нажмите 'Отмена'")


@router.callback_query(F.data.startswith("genvideo "))
async def add_source(call: CallbackQuery, state: FSMContext):
    """Работса с FSMGenerateVideo.Отправляет пользователю инлайн кнопки с выбором
    вариантов для генераторов видео
    """
    _, generating_video = call.data.split(" ")

    await state.set_state(FSMGenerateVideo.source)
    await call.message.edit_reply_markup(reply_markup=None)
    if generating_video == settings.video_generation.vheer.CALLBACK_INLINE_BUTTON:
        await state.update_data(
            source=settings.video_generation.vheer.CALLBACK_INLINE_BUTTON
        )
        await call.message.answer(
            text="Доступные варианты",
            reply_markup=get_buttons_for_generating_video_for_vheer(),
        )


@router.callback_query(
    F.data.startswith(f"{settings.video_generation.vheer.CALLBACK_INLINE_BUTTON} ")
)
async def add_image(call: CallbackQuery, state: FSMContext):
    _, flag = call.data.split(" ")

    await call.message.edit_reply_markup(reply_markup=None)

    # Если пользователь сделал выбор сделать видое только по фото то встаем в description
    if flag == "img":
        await state.set_state(FSMGenerateVideo.description)
        await state.update_data(description=True)
    await call.message.answer(
        "Скидывайте картинку для которой хотите сделать видео",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(FSMGenerateVideo.image)


@router.message(FSMGenerateVideo.image)
async def add_description(message: Message, state: FSMContext):
    """Работса с FSMGenerateVideo.Просит пользователя ввести описание для
    генерации изображения.
    """
    if message.content_type == "photo":
        photo_phile = message.photo[-1]
        file_info = await bot.get_file(photo_phile.file_id)
        file_path: str = file_info.file_path
        _, file_name = file_path.split("/")

        image_path: str = f"{settings.VIDEO_GENERATE_IMAGE_PATH}{file_name}"

        await state.update_data(image=image_path)

        data = await state.get_data()
        await message.bot.download(
            file=message.photo[-1].file_id,
            destination=f"{settings.VIDEO_GENERATE_IMAGE_PATH}{file_name}",
        )
        if data.get("description", None):
            await get_video_generation(message=message, state=state)
        else:
            await state.set_state(FSMGenerateVideo.prompt)
            await message.answer(
                "Введите описание того что хотите увидеть для изображения"
            )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Скидываемый файл должен быть изображением, в формате .JPEG или .PNG.Размер до 50 мб.",
        )


@router.message(FSMGenerateVideo.prompt, F.text)
async def get_video_generation(message: Message, state: FSMContext):
    """Работса с FSMGenerateVideo.Отправляет пользователю скаченое видео."""

    # Встаем в состояние counter_progress для отслеживание прогресса загрузки
    await state.set_state(FSMGenerateVideo.counter_progress)
    await state.update_data(counter_progress=1)

    data: Dict = await state.get_data()
    source: str = data.get("source")
    image_path: str = data.get("image")
    description = data.get("description", None)

    prompt = None
    # Если пользователь сделал выбор сгененрировать по фото и описанию то берем описание
    # из message
    if not description:
        prompt: str = message.text

    await message.answer(
        "Обработка может занять от 30 секунд до 5 минут. Пожалуйста, наберитесь терпения"
    )

    if source == settings.video_generation.vheer.CALLBACK_INLINE_BUTTON:

        await state.set_state(FSMGenerateVideo.counter_progress)
        await state.update_data(counter_progress=0)

        loop: AbstractEventLoop = asyncio.get_event_loop()

        # Функция для отслеживания прогресса
        update_prgoress: Callable = make_update_progress(loop=loop, state=state)

        # Функция для отслеживания пользователем нажатия кнопки отмены
        cancel_chek: Callable = make_cancel_chek(loop=loop, state=state)

        video_path: str = (
            f"{settings.VIDEO_GENERATE_VIDEO_PATH}{random.randint(0, 1000)}.mp4"
        )
        description_url = (
            settings.video_generation.vheer.PROMPT_IMG_URL if description else None
        )
        progressing_task: Future = loop.run_in_executor(
            None,
            create_video_by_is_vheer,
            settings.video_generation.vheer.VIDEO_URL,
            settings.PATH_COOGLE_DRIVER,
            image_path,
            video_path,
            settings.video_generation.vheer.VIDEO_DATA,
            prompt,
            update_prgoress,
            cancel_chek,
            description_url,
        )

        msg: str = "Обработка запроса:\n\n📥Генерация Описания - Ожидайте "
        end_mess: str = "\n📥Генерация Bидео - Ожидайте  0%"
        description_message: str = (
            "Обработка запроса:\n\n✅Генерация Описания - Завершено\n📥Генерация Bидео - Ожидайте "
        )
        progress_message: Message = await message.answer(
            text=msg,
        )

        total: int = settings.video_generation.vheer.TOTAL_STEP
        new_counter: int = -1

        # для отображение прогресса если идет обращение с сайту для генерации описания
        counter_list: List[str] = ["", ".", "..", "...", "...."]
        count: int = 0
        while not progressing_task.done():
            data: Dict = await state.get_data()

            if data.get("cancel", None):
                break

            counter: int = data.get("counter_progress")

            if new_counter != counter:
                new_counter = counter
                try:
                    counter = (counter / total) * 100
                    if counter <= 20 and description:
                        if count == 5:
                            count = 0
                        count += 1
                        await asyncio.sleep(0.5)

                        await progress_message.edit_text(
                            f"{msg}{counter_list[count]}{end_mess}"
                        )
                    else:
                        await progress_message.edit_text(
                            f"{description_message}{counter:.2f} %"
                        )
                except Exception as err:
                    print(err)
                    pass
            await asyncio.sleep(0.5)

        data = await state.get_data()
        if data.get("cancel", None):

            msg = "Подождите идет процесс отмены генерации видео "
            cancel_message: Message = await message.answer(text=msg)
            counter_list: List[str] = ["", ".", "..", "...", "...."]
            count: int = -1
            while not progressing_task.done():
                try:
                    if count == 5:
                        count = 0

                    count += 1
                    text: str = f"{msg}{counter_list[count]}"
                    await asyncio.sleep(1)
                    await cancel_message.edit_text(text=text)
                except Exception:
                    pass
            await state.clear()

            if os.path.exists(video_path):
                os.remove(video_path)

            await bot.send_message(
                chat_id=message.chat.id,
                text="Генерация Bидео прервана....",
                reply_markup=ReplyKeyboardRemove(),
            )
            await main(message=message)
        else:
            video_path = await progressing_task
            if video_path.get("message", None):

                await progress_message.edit_text(
                    "Обработка запроса:\n\n✅Генерация"
                    " Описания - Завершено\n✅Генерация Видео - Завершено\n\nИдет выгружение "
                    "видео в телеграм"
                )
                await asyncio.sleep(1)

                video_path: str = video_path.get("message")
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=FSInputFile(path=video_path),
                    reply_markup=ReplyKeyboardRemove(),
                )
                await main(message=message)

                os.remove(video_path)
                os.remove(image_path)
                await state.clear()
            else:
                await state.clear()
                await message.answer(text=video_path.get("error"))
