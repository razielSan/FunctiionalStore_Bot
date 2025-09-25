from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter

from keyboards.inline_kb import get_buttons_for_generating_passwords


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Генерация паролей")
async def main(message: Message):
    """Возвращает пользователю инлайн клавиатуру с выбором вариантов генерации паролей."""

    print("ok")
    await message.answer(
        text="Доступные варианты",
        reply_markup=get_buttons_for_generating_passwords(),
    )
