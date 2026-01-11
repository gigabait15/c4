# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

# Установка системных зависимостей для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev --no-install-project

# Копируем исходный код
COPY . .

# Устанавливаем проект
RUN uv sync --frozen --no-dev

# ============================================
# Образ для FastAPI
# ============================================
FROM base AS api

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================
# Образ для Telegram бота
# ============================================
FROM base AS bot

CMD ["uv", "run", "python", "-m", "bot.main"]

# ============================================
# Образ для миграций
# ============================================
FROM base AS migrations

CMD ["uv", "run", "alembic", "upgrade", "head"]

