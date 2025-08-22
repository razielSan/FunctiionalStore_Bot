import sys
import zipfile
import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.reply_kb import get_cancel_button, get_start_button_bot
from extension import bot
from errors import chek_number_is_positivity
from functions import find_image_with_goole_and_save_image, delete_images_and_archive


router = Router(name=__name__)


# Логика для поиска изображений
class FindImage(StatesGroup):
    """FSM для поиска изображений."""

    name = State()
    count = State()


@router.message(F.text == "Поиск Изображений")
async def start_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Просит у пользователя ввести название изображения."""
    await message.answer(
        "Введите название изображение которое хотите найти",
        reply_markup=get_cancel_button(),
    )
    await state.set_state(FindImage.name)


@router.message(FindImage.name, F.text == "Отмена")
@router.message(FindImage.count, F.text == "Отмена")
async def cancel_find_image_handler(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Отменяет поиск изображений."""
    current_state = await state.get_state()

    if current_state is None:
        return

    await state.clear()
    await message.answer("Поиск изображений отменен")
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(FindImage.name, F.text)
async def add_name_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Добавляет имя FSM FindImage и просит у пользователя
    ввести количество изображений для поиска."""
    await state.update_data(name=message.text)

    await message.answer("Введите количество изображений которые хотите найти")
    await state.set_state(FindImage.count)


@router.message(FindImage.count, F.text)
async def finsh_find_image(message: Message, state: FSMContext):
    """Работа с FSM FindImage.Скидывает zip архив пользователю найденных изображений."""
    number, mess = chek_number_is_positivity(number=message.text)
    if not number:
        await message.answer(
            text=f"{mess['err']}\n\n"
            "Введите снова количество изображений которые хотите найти"
        )
    else:
        await message.answer(text="Идет Поиск")
        data = await state.get_data()
        name = data["name"]
        path = os.path.join(sys.path[0], f"{name}.zip")

        count_pictures = number
        filters = {"size": "large"}
        result = find_image_with_goole_and_save_image(
            name=name,
            count=count_pictures,
            filters=filters,
            path=sys.path[0],
        )
        if result:

            # Указываем имена изображений
            list_images_name = []
            for number in range(1, count_pictures + 1):
                list_images_name.append(f"{number:06}.jpg")

            # Сохраняем изображения в архив
            with zipfile.ZipFile(f"{name}.zip", "w") as rf:
                try:
                    for file_path in list_images_name:
                        rf.write(file_path)
                except Exception:
                    pass

            await bot.send_document(
                chat_id=message.chat.id,
                document=FSInputFile(path=path),
                caption="Вот ваша скаченные изображения",
            )

            delete_images_and_archive(
                path_archive=path,
                count_images=count_pictures,
            )

            await state.clear()
            await start_find_image(
                message=message,
                state=state,
            )
