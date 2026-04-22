"""Обработчик сообщений с ссылками на Яндекс.Музыку.

Реагирует на текстовые сообщения, содержащие ссылки
на треки, и возвращает информацию в формате MarkdownV2.
"""

import logging
import re

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from services.url_parser import extract_track_id, is_yandex_music_link
from services.yandex_music_service import (
    TrackNotFoundError,
    TrackServiceError,
    get_track_info,
)

logger = logging.getLogger(__name__)

router = Router(name="track_router")

# ── Утилиты MarkdownV2 ───────────────────────────────────

# Символы, которые нужно экранировать в MarkdownV2
_MD2_ESCAPE_CHARS = re.compile(r"([_*\[\]()~`>#+\-=|{}.!])")


def _escape_md2(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2.

    Args:
        text: Исходный текст.

    Returns:
        Текст с экранированными спецсимволами.
    """
    return _MD2_ESCAPE_CHARS.sub(r"\\\1", text)


def _format_track_response(title: str, artists: str, duration: str) -> str:
    """Форматирует ответ с информацией о треке в MarkdownV2.

    Шаблон: 🎵 *Название трека* — _Исполнитель_ [⏱ 00:00]

    Args:
        title: Название трека.
        artists: Имена артистов.
        duration: Длительность в формате MM:SS.

    Returns:
        Отформатированная строка в MarkdownV2.
    """
    escaped_title = _escape_md2(title)
    escaped_artists = _escape_md2(artists)
    escaped_duration = _escape_md2(duration)

    return (
        f"🎵 *{escaped_title}* — _{escaped_artists}_ "
        f"\\[⏱ {escaped_duration}\\]"
    )


# ── Хендлеры ──────────────────────────────────────────────


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    """Обработчик команды /start."""
    welcome_text = (
        "🎶 *Добро пожаловать в UpSound Bot\\!*\n\n"
        "Отправьте мне ссылку на трек из Яндекс\\.Музыки, "
        "и я покажу информацию о нём\\.\n\n"
        "📎 Поддерживаемые форматы ссылок:\n"
        "• `music\\.yandex\\.ru/album/.../track/...`\n"
        "• `music\\.yandex\\.ru/track/...`\n\n"
        "🎧 _Powered by UpSound_"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN_V2)
    logger.info(
        "Пользователь %s (%s) запустил бота",
        message.from_user.id if message.from_user else "unknown",
        message.from_user.username if message.from_user else "unknown",
    )


@router.message(F.text)
async def handle_track_link(message: types.Message) -> None:
    """Обработчик текстовых сообщений с ссылками на Яндекс.Музыку.

    Извлекает track_id, получает информацию о треке
    и отправляет форматированный ответ.
    """
    if not message.text:
        return

    if not is_yandex_music_link(message.text):
        await message.answer(
            "❌ *Некорректная ссылка*\n\n"
            "Я принимаю только ссылки на треки из Яндекс\\.Музыки\\.\n\n"
            "📎 Примеры корректных ссылок:\n"
            "• `music\\.yandex\\.ru/album/\\.\\.\\./track/\\.\\.\\.`\n"
            "• `music\\.yandex\\.ru/track/\\.\\.\\.`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    user_id = message.from_user.id if message.from_user else "unknown"
    logger.info(
        "Получена ссылка от пользователя %s: %s",
        user_id,
        message.text[:100],
    )

    track_id = extract_track_id(message.text)
    if not track_id:
        await message.answer("❌ Не удалось извлечь ID трека из ссылки\\.")
        return

    # Индикатор загрузки
    processing_msg = await message.answer("⏳ Загружаю информацию о треке\\.\\.\\.")

    try:
        track_info = await get_track_info(track_id)

        response = _format_track_response(
            title=track_info.title,
            artists=track_info.artists,
            duration=track_info.duration,
        )

        await processing_msg.edit_text(
            response,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        logger.info(
            "Информация о треке отправлена пользователю %s: %s — %s",
            user_id,
            track_info.title,
            track_info.artists,
        )

    except TrackNotFoundError as exc:
        error_msg = _escape_md2(str(exc))
        await processing_msg.edit_text(
            f"❌ {error_msg}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.warning("Трек не найден для пользователя %s: %s", user_id, exc)

    except TrackServiceError as exc:
        error_msg = _escape_md2(str(exc))
        await processing_msg.edit_text(
            f"⚠️ {error_msg}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.error("Ошибка сервиса для пользователя %s: %s", user_id, exc)

    except Exception as exc:
        await processing_msg.edit_text(
            "💥 Произошла непредвиденная ошибка\\. Попробуйте позже\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.exception(
            "Непредвиденная ошибка при обработке запроса от %s: %s",
            user_id,
            exc,
        )
