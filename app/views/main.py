from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter

from keyboards.reply_kb import get_start_button_bot


router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "/start")
async def main(message: Message):
    """Вызывает генерацтию главного меню бота."""
    await message.answer(
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )
