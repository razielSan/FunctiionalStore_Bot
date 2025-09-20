import json
import os
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import get_button_ip
from keyboards.reply_kb import get_cancel_button
from functions import get_user_info
from errors import Ip4Handler, Ipi6Handler
from functions import get_ip_info
from config import settings
from extension import bot


router = Router(name=__name__)


class IpInfo(StatesGroup):
    source = State()
    info = State()


@router.message(StateFilter(None), F.text == "Информация по ip")
async def main_user_info(message: Message):
    """Возвращает инлайн кнопки выбора доступных вариантов сбора информации по ip"""

    await message.answer(
        "Доступные варианты",
        reply_markup=get_button_ip(),
    )


@router.message(IpInfo.info, F.text == "Отмена")
async def cancel_user_info_handler(message: Message, state: FSMContext):
    """Работа с FSM IpInfo.Отменяет все действия."""

    current_state = await state.get_data()

    if current_state is None:
        return

    await state.clear()
    await message.answer(
        text="Сбор информации по ip отменен", reply_markup=ReplyKeyboardRemove()
    )
    await main_user_info(message=message)


@router.callback_query(F.data.startswith("ip "))
async def add_source_ip(call: CallbackQuery, state: FSMContext):
    _, source = call.data.split(" ")

    await state.set_state(IpInfo.source)
    await state.update_data(source=source)
    await state.set_state(IpInfo.info)
    if source == "telegram":
        await add_info_ip(
            message=call.message,
            state=state,
        )
    elif source == "ip_info":
        await call.message.answer(
            text="Введите номер ip, о котором хотите узнать информацию в формате\n\n"
            "192.168.0.3 - ip4\n"
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
            reply_markup=get_cancel_button(),
        )


@router.message(IpInfo.info, F.text)
async def add_info_ip(message: Message, state: FSMContext):
    """Возвращает пользователю информацию по ip."""
    data = await state.get_data()

    source = data["source"]

    if source == "telegram":
        data = json.loads(message.json())
        api_id = data["chat"]["id"]
        first_name = data["chat"]["first_name"]
        user_name = data["chat"]["username"]
        last_name = data["chat"]["last_name"]

        user_info = get_user_info(
            api_id=api_id,
            first_name=first_name,
            user_name=user_name,
            last_name=last_name,
        )

        await state.clear()
        await message.answer(text=user_info, parse_mode="HTML")
    elif source == "ip_info":
        data = message.text
        if data.find(".") >= 0:
            data = data.split(".")
        elif data.find(":") >= 0:
            data = data.split(":")
        if len(data) == 4 or len(data) == 8:
            try:
                if len(data) == 4:
                    Ip4Handler.parse_obj({"ip4": message.text})
                else:
                    Ipi6Handler.parse_obj({"ip6": message.text})
            except ValueError as err:
                data = json.loads(err.json())
                mess = data[0]["msg"]
                await message.answer(
                    text=f"{mess}\n\nВведите снова номер ip, о котором хотите "
                    "узнать информацию в формате\n\n"
                    "192.168.0.3 - ip4\n"
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
                )
            else:
                path, data = get_ip_info(
                    ip=message.text,
                    url=settings.ip_info.ipapi.ULR_IP_INFO,
                    acces_key=settings.ip_info.ipapi.AccessKey,
                )
                await state.clear()
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=FSInputFile(path=path),
                    caption=data,
                    reply_markup=ReplyKeyboardRemove(),
                )

                os.remove(os.path.join(Path(__file__).parent.parent, "file.json"))
                await main_user_info(message=message)

        else:
            await message.answer(
                text="Неверный формат ввода\n\nВведите снова номер ip, о котором хотите узнать информацию в формате\n\n"
                "192.168.0.3 - ip4\n"
                "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
            )
