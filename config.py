"""Конфигурация приложения UpSound Bot.

Загружает переменные окружения из .env и предоставляет
централизованный доступ к настройкам бота.
"""

import io
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    sys.exit("TELEGRAM_BOT_TOKEN не задан в .env")

# ── Yandex Music ──────────────────────────────────────────
YANDEX_MUSIC_TOKEN: str = os.getenv("YANDEX_MUSIC_TOKEN", "")
if not YANDEX_MUSIC_TOKEN:
    sys.exit("YANDEX_MUSIC_TOKEN не задан в .env")

# ── Logging ───────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def setup_logging() -> None:
    """Настраивает структурированное логирование (JSON-friendly)."""
    # Оборачиваем stdout в UTF-8, чтобы emoji и кириллица
    # корректно выводились на Windows (cp1251 по умолчанию)
    utf8_stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    handler = logging.StreamHandler(utf8_stdout)

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=(
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[handler],
    )
