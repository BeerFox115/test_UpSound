# ── Сборка ────────────────────────────────────────────────
FROM python:3.12-slim AS base

# Не создавать .pyc файлы, не буферизовать stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Зависимости ───────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Код приложения ────────────────────────────────────────
COPY . .

# ── Запуск ────────────────────────────────────────────────
CMD ["python", "main.py"]
