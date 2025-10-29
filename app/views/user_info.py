import json
from typing import Optional, Dict

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    FSInputFile,
)
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.inline_kb import get_button_ip
from keyboards.reply_kb import get_cancel_button, get_start_button_bot
from errors_handlers.user_info import Ip4Handler, Ipi6Handler
from bot_functions.user_info import get_user_info, get_ip_info
from settings.config import settings
from extension import bot
from settings.response import ResponseData


router: Router = Router(name=__name__)


class IpInfo(StatesGroup):
    spam: State = State()
    source: State = State()
    info: State = State()


@router.message(StateFilter(None), F.text == "Информация по ip")
async def main_user_info(message: Message):
    """Возвращает инлайн кнопки выбора доступных вариантов сбора информации по ip"""

    await message.answer(
        "Доступные варианты",
        reply_markup=get_button_ip(),
    )


@router.message(IpInfo.spam, F.text)
async def get_message_user_info(message: Message, state: FSMContext):
    """Работа с FSM IpInfo.Отправляет пользователю сообщение при обработке информации."""
    await message.reply("Идет обработка запроса, пожалуйста подождите...")


@router.message(IpInfo.info, F.text == "Отмена")
async def cancel_user_info_handler(message: Message, state: FSMContext):
    """Работа с FSM IpInfo.Отменяет все действия."""

    current_state: Dict = await state.get_data()

    if current_state is None:
        return

    await state.clear()
    await message.answer(
        text="Сбор информации по ip отменен",
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text="Главное меню бота",
        reply_markup=get_start_button_bot(),
    )


@router.callback_query(F.data.startswith("ip "))
async def add_source_ip(call: CallbackQuery, state: FSMContext):
    _, source = call.data.split(" ")

    await state.set_state(IpInfo.source)
    await state.update_data(source=source)

    await state.set_state(IpInfo.info)
    await call.message.edit_reply_markup(reply_markup=None)
    if source == "telegram":
        await add_info_ip(
            message=call.message,
            state=state,
        )
        return
    elif source == "ip_info":
        await call.message.answer(
            text="Введите номер ip, о котором хотите узнать информацию в "
            "формате\n\n"
            "192.168.0.3 - ip4\n"
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
            reply_markup=get_cancel_button(),
        )


@router.message(IpInfo.info, F.text)
async def add_info_ip(message: Message, state: FSMContext):
    """Возвращает пользователю информацию по ip."""
    data: Dict = await state.get_data()

    source: Dict = data["source"]

    if source == "telegram":

        # Формируем данные по ip telegram
        data = json.loads(message.json())
        api_id: int = data["chat"]["id"]
        first_name: str = data["chat"]["first_name"]
        user_name: str = data["chat"]["username"]
        last_name: Optional[str] = data["chat"]["last_name"]

        user_info: str = await get_user_info(
            api_id=api_id,
            first_name=first_name,
            user_name=user_name,
            last_name=last_name,
        )

        await state.clear()
        await message.answer(text=user_info, parse_mode="HTML")
    elif source == "ip_info":

        # Встаем в состояние spam для отловки сообщений пользователя при
        # обработке запроса
        await state.set_state(IpInfo.spam)

        data = message.text

        await message.answer(
            "Идет обработка запроса.Подождите...",
            reply_markup=ReplyKeyboardRemove(),
        )

        # Проверяем подходят ли даныые под формат ip4 или ip6
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

                await state.set_state(IpInfo.info)

                data = json.loads(err.json())
                mess: str = data[0]["msg"]
                await message.answer(
                    text=f"{mess}\n\nВведите снова номер ip, о котором хотите "
                    "узнать информацию в формате\n\n"
                    "192.168.0.3 - ip4\n"
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
                    reply_markup=get_cancel_button(),
                )
            else:

                # Формируем данные запроса и получаем данные по ip
                url: str = settings.ip_info.ipapi.ULR_IP_INFO.format(
                    ip=message.text,
                    access_key=settings.ip_info.ipapi.AccessKey,
                )
                data_ip: ResponseData = await get_ip_info(
                    url=url,
                    path_folder_flag_country=settings.ip_info.PATH_FOLDER_FLAG_COUNTRY,
                    path_folder_none_flag_img=settings.ip_info.PATH_FOLDER_NONE_FLAG_IMG,
                )

                if data_ip.message:

                    path_img: str = str(data_ip.message[0])
                    data: str = data_ip.message[1]

                    await state.clear()
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=FSInputFile(path=path_img),
                        caption=data,
                        reply_markup=ReplyKeyboardRemove(),
                    )

                    await bot.send_message(
                        chat_id=message.chat.id,
                        text="Главное меню бота",
                        reply_markup=get_start_button_bot(),
                    )
                else:
                    await state.set_state(IpInfo.info)
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text=f"{data_ip.error}\n\nВведите снова номер ip, о "
                        "котором хотите "
                        "узнать информацию в формате\n\n"
                        "192.168.0.3 - ip4\n"
                        "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
                        reply_markup=get_cancel_button(),
                    )

        else:
            await state.set_state(IpInfo.info)

            await message.answer(
                text="Неверный формат ввода\n\nВведите снова номер ip, о "
                "котором хотите узнать информацию в формате\n\n"
                "192.168.0.3 - ip4\n"
                "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - ip6",
                reply_markup=get_cancel_button(),
            )
