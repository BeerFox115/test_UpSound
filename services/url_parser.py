"""Парсер URL-ссылок Яндекс.Музыки.

Извлекает track_id из различных форматов ссылок:
- music.yandex.ru/album/12345/track/67890
- music.yandex.ru/track/67890
- music.yandex.com/album/12345/track/67890?from=search
- Разные доменные зоны: .ru, .com, .by, .kz, .uz
"""

import logging
import re

logger = logging.getLogger(__name__)

# Паттерн для извлечения track_id из URL Яндекс.Музыки
_YANDEX_MUSIC_PATTERN: re.Pattern[str] = re.compile(
    r"music\.yandex\.(?:ru|com|by|kz|uz)"  # домен
    r"/(?:album/\d+/)?"                     # опциональный album/ID/
    r"track/(\d+)",                         # track/ID — захватываем ID
    re.IGNORECASE,
)

# Паттерн для определения, содержит ли текст ссылку на Яндекс.Музыку
_YANDEX_MUSIC_DETECT_PATTERN: re.Pattern[str] = re.compile(
    r"music\.yandex\.(?:ru|com|by|kz|uz)/.*track/\d+",
    re.IGNORECASE,
)


def extract_track_id(text: str) -> str | None:
    """Извлекает track_id из текста, содержащего ссылку Яндекс.Музыки.

    Args:
        text: Текст сообщения, потенциально содержащий URL.

    Returns:
        track_id как строку, или None если ссылка не найдена.
    """
    if not text:
        return None

    match = _YANDEX_MUSIC_PATTERN.search(text)
    if not match:
        logger.debug("Ссылка на Яндекс.Музыку не найдена в тексте: %s", text[:100])
        return None

    track_id = match.group(1)
    logger.info("Извлечён track_id=%s из текста", track_id)
    return track_id


def is_yandex_music_link(text: str) -> bool:
    """Проверяет, содержит ли текст ссылку на трек Яндекс.Музыки.

    Args:
        text: Текст для проверки.

    Returns:
        True, если текст содержит ссылку на трек.
    """
    if not text:
        return False
    return bool(_YANDEX_MUSIC_DETECT_PATTERN.search(text))
