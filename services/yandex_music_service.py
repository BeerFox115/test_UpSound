"""Асинхронный сервис для работы с API Яндекс.Музыки.

Предоставляет функцию получения информации о треке
по его ID с обработкой всех возможных ошибок.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from yandex_music import ClientAsync
from yandex_music.exceptions import (
    BadRequestError,
    NetworkError,
    NotFoundError,
    UnauthorizedError,
)

from config import YANDEX_MUSIC_TOKEN

logger = logging.getLogger(__name__)

# ── Модели данных ─────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TrackInfo:
    """Информация о треке."""

    title: str
    artists: str
    duration: str  # формат MM:SS
    cover_url: str | None = None


class TrackNotFoundError(Exception):
    """Трек не найден или недоступен."""


class TrackServiceError(Exception):
    """Общая ошибка сервиса Яндекс.Музыки."""


# ── Клиент (lazy-init singleton) ──────────────────────────

_client: ClientAsync | None = None


async def _get_client() -> ClientAsync:
    """Возвращает инициализированный асинхронный клиент Яндекс.Музыки."""
    global _client
    if _client is None:
        logger.info("Инициализация клиента Яндекс.Музыки...")
        _client = ClientAsync(YANDEX_MUSIC_TOKEN)
        await _client.init()
        logger.info("Клиент Яндекс.Музыки инициализирован успешно")
    return _client


# ── Основная функция ──────────────────────────────────────


def _format_duration(duration_ms: int | None) -> str:
    """Конвертирует длительность из миллисекунд в формат MM:SS.

    Args:
        duration_ms: Длительность в миллисекундах.

    Returns:
        Строка формата "MM:SS" или "00:00" если данных нет.
    """
    if not duration_ms:
        return "00:00"

    total_seconds = duration_ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


async def get_track_info(track_id: str) -> TrackInfo:
    """Получает информацию о треке по его ID.

    Args:
        track_id: Идентификатор трека в Яндекс.Музыке.

    Returns:
        Объект TrackInfo с информацией о треке.

    Raises:
        TrackNotFoundError: Трек не найден или недоступен.
        TrackServiceError: Ошибка при обращении к API.
    """
    if not track_id or not track_id.isdigit():
        raise TrackNotFoundError(f"Некорректный track_id: {track_id}")

    try:
        client = await _get_client()
        tracks = await client.tracks([track_id])

        if not tracks:
            logger.warning("Трек track_id=%s не найден", track_id)
            raise TrackNotFoundError(
                f"Трек с ID {track_id} не найден. "
                "Возможно, он удалён или недоступен в вашем регионе."
            )

        track = tracks[0]

        # Название
        title = track.title or "Без названия"

        # Артисты (через запятую)
        artists = "Неизвестный исполнитель"
        if track.artists:
            artists = ", ".join(
                artist.name for artist in track.artists if artist.name
            )

        # Длительность
        duration = _format_duration(track.duration_ms)

        # Обложка
        cover_url = None
        if track.cover_uri:
            cover_url = f"https://{track.cover_uri.replace('%%', '400x400')}"

        track_info = TrackInfo(
            title=title,
            artists=artists,
            duration=duration,
            cover_url=cover_url,
        )

        logger.info(
            "Получена информация о треке: %s — %s [%s]",
            title,
            artists,
            duration,
        )
        return track_info

    except NotFoundError as exc:
        logger.warning("Трек track_id=%s не найден: %s", track_id, exc)
        raise TrackNotFoundError(
            f"Трек с ID {track_id} не найден. "
            "Возможно, он удалён или недоступен в вашем регионе."
        ) from exc

    except UnauthorizedError as exc:
        logger.error("Ошибка авторизации Яндекс.Музыки: %s", exc)
        raise TrackServiceError(
            "Ошибка авторизации. Проверьте YANDEX_MUSIC_TOKEN в .env"
        ) from exc

    except BadRequestError as exc:
        logger.error("Некорректный запрос к API: %s", exc)
        raise TrackServiceError(
            f"Некорректный запрос для track_id={track_id}"
        ) from exc

    except NetworkError as exc:
        logger.error("Сетевая ошибка при запросе трека: %s", exc)
        raise TrackServiceError(
            "Сетевая ошибка при обращении к API Яндекс.Музыки. "
            "Попробуйте позже."
        ) from exc

    except Exception as exc:
        logger.exception(
            "Непредвиденная ошибка при получении трека track_id=%s",
            track_id,
        )
        raise TrackServiceError(
            f"Непредвиденная ошибка: {exc}"
        ) from exc
