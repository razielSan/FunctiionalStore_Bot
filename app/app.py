import asyncio


from extension import bot, dp
from settings.config import settings
from logging_handler.main import rout_logging
from views.main import router as main_router
from views.weather_forecast import router as weather_forecast_router
from views.find_image import router as find_image_router
from views.find_video import router as find_video_router
from views.user_info import router as user_info_router
from views.get_proxies import router as proxies_router
from views.recommender_system import router as recommender_system_router
from views.generate_password import router as generate_password_router


async def on_startup():
    """Выводит информацию о запуске бота."""
    print("Бот запущен")


async def main():
    """Собирает все части приложения и запускает бота."""

    rout_logging.info("Бот запущен")
    await bot.set_my_commands(settings.BOT_COMMAND)
    await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(on_startup)
    dp.include_router(generate_password_router)
    dp.include_router(recommender_system_router)
    dp.include_router(proxies_router)
    dp.include_router(find_video_router)
    dp.include_router(find_image_router)
    dp.include_router(weather_forecast_router)
    dp.include_router(user_info_router)
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
