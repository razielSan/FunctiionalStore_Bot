from aiogram import Bot, Dispatcher

from config import settings


bot = Bot(token=settings.TOKEN)

dp = Dispatcher()
