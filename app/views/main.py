from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile

from keyboards.reply_kb import get_start_button_bot
from extension import bot


router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "/start")
async def main(message: Message):
    """Вызывает генерацтию главного меню бота."""
    await message.answer(
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.message(StateFilter(None), F.text == "s")
async def main2(message: Message):
    """Вызывает генерацтию главного меню бота."""
    path = "D:\ProgrammingProjects\Python\Bot\Project\BOT_PROJECT\FunctiionalStore_Bot\\app\static/img/none.png"
    await bot.send_photo(chat_id=message.chat.id, photo=FSInputFile(path))