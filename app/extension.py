from aiogram import Bot, Dispatcher

from settings.config import settings


bot = Bot(token=settings.TOKEN)

dp = Dispatcher()
