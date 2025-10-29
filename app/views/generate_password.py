from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter

from keyboards.inline_kb import get_buttons_for_generating_passwords
from functions import get_generateing_simple_or_difficult_password


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == "Генерация паролей")
async def main(message: Message):
    """Возвращает пользователю инлайн клавиатуру с выбором вариантов генерации паролей."""

    await message.answer(
        text="Доступные варианты",
        reply_markup=get_buttons_for_generating_passwords(),
    )


@router.callback_query(F.data.startswith("password "))
async def get_generating_password(call: CallbackQuery):
    """Возвращает сгенерированный пароль."""

    _, password = call.data.split(" ")
    passwords: str = get_generateing_simple_or_difficult_password(
        step=3, password=password
    )

    await call.message.answer(text=passwords)
