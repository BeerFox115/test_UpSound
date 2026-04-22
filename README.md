# 🎵 UpSound Bot

Telegram-бот для музыкального агентства **UpSound**.  
Отправьте ссылку на трек из Яндекс.Музыки — бот вернёт название, исполнителя и длительность.

## 📋 Возможности

- Парсинг ссылок Яндекс.Музыки (несколько форматов URL)
- Получение информации о треке через Yandex Music API
- Ответ в красивом формате MarkdownV2: `🎵 *Трек* — _Артист_ [⏱ 03:45]`
- Обработка ошибок (трек не найден, недоступен, ошибка сети)
- Docker-контейнеризация

## 🚀 Быстрый старт

### 1. Получите токен Telegram-бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям: задайте имя и username бота
4. Скопируйте полученный **API token**

### 2. Получите токен Яндекс.Музыки

#### Способ A: Через скрипт (рекомендуется)

```bash
# Из корня проекта
python get_token.py
```

Скрипт попросит открыть URL в браузере и ввести код.  
После авторизации вы получите `access_token` — это и есть ваш токен.

#### Способ B: Через браузер (ручной)

1. Откройте [music.yandex.ru](https://music.yandex.ru) и войдите в аккаунт
2. Откройте DevTools (F12) → вкладка **Network**
3. Обновите страницу и найдите запросы к API
4. В заголовках найдите `Authorization: OAuth <ваш_токен>`

### 3. Настройте окружение

```bash
cd upsound_bot

# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env — вставьте свои токены
```

Содержимое `.env`:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
YANDEX_MUSIC_TOKEN=y0_AgAAAA...
LOG_LEVEL=INFO
```

### 4. Запуск

#### Через Docker (рекомендуется)

```bash
docker compose up -d --build
```

Посмотреть логи:
```bash
docker compose logs -f bot
```

Остановить:
```bash
docker compose down
```

#### Локально

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите бота
python main.py
```

#### Через uv (если используете uv)

```bash
uv pip install -r requirements.txt
uv run main.py
```

## 📂 Структура проекта

```
upsound_bot/
├── main.py                          # Точка входа — запуск бота
├── config.py                        # Конфигурация из .env
├── handlers/
│   ├── __init__.py
│   └── track_handler.py             # Хендлер ссылок + /start
├── services/
│   ├── __init__.py
│   ├── url_parser.py                # Regex-парсер URL
│   └── yandex_music_service.py      # API Яндекс.Музыки
├── .env.example                     # Шаблон переменных окружения
├── requirements.txt                 # Зависимости Python
├── Dockerfile                       # Docker-образ
├── docker-compose.yml               # Docker Compose
└── README.md                        # Эта документация
```

## 🔗 Поддерживаемые форматы ссылок

| Формат | Пример |
|--------|--------|
| Полная ссылка с альбомом | `https://music.yandex.ru/album/12345/track/67890` |
| Прямая ссылка на трек | `https://music.yandex.ru/track/67890` |
| С параметрами | `https://music.yandex.ru/album/12345/track/67890?from=search` |
| Другие домены | `music.yandex.com`, `music.yandex.by`, `music.yandex.kz` |

## 🛠 Технологии

- **Python 3.12+**
- **[aiogram 3.x](https://docs.aiogram.dev/)** — асинхронный Telegram Bot API
- **[yandex-music](https://github.com/MarshalX/yandex-music-api)** — клиент Yandex Music API
- **python-dotenv** — управление переменными окружения
- **Docker** — контейнеризация

## 📄 Лицензия

MIT © UpSound
