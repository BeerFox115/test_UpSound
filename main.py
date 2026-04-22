"""UpSound Bot — Telegram-бот для музыкального агентства UpSound.

Точка входа приложения. Инициализирует бота, подключает
обработчики и запускает long polling.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TELEGRAM_BOT_TOKEN, setup_logging
from handlers.track_handler import router as track_router

logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная асинхронная функция запуска бота."""
    setup_logging()
    logger.info("Запуск UpSound Bot...")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )

    dp = Dispatcher()
    dp.include_router(track_router)

    logger.info("Бот инициализирован, начинаю polling...")

    try:
        # Удаляем вебхук и пропускаем накопленные апдейты
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (Ctrl+C)")
        sys.exit(0)
