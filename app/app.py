import asyncio


from extension import bot, dp
from config import settings
from views.main import router as main_router
from views.weather_forecast import router as weather_forecast_router
from views.find_image import router as find_image_router
from views.generate_image import router as generate_image_router
from views.image_descriptions import router as image_description_router
from views.find_video import router as find_video_router


async def on_startup():
    """Выводит информацию о запуске бота."""
    print("Бот запущен")


async def main():
    """Собирает все части приложения и запускает бота."""
    await bot.set_my_commands(settings.BOT_COMMAND)
    await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)
    dp.include_router(find_video_router)
    dp.include_router(image_description_router)
    dp.include_router(generate_image_router)
    dp.include_router(find_image_router)
    dp.include_router(weather_forecast_router)
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
