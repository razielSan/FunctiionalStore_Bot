from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter

from keyboards.inline_kb import get_buttons_for_generating_passwords
from keyboards.reply_kb import get_start_button_bot

from bot_functions.generate_password import get_generateing_simple_or_difficult_password
from settings.response import ResponseData
from extension import bot


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
    passwords: ResponseData = await get_generateing_simple_or_difficult_password(
        step=3, password_hard=password
    )

    await call.message.edit_reply_markup(
        reply_markup=None,
    )

    await call.message.answer(text=passwords.message)

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )
