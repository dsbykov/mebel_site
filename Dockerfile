# --- Builder stage ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Минимальные инструменты для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ставим uv
RUN python -m pip install --upgrade pip && pip install uv
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы зависимостей раньше кода (для кэширования слоёв)
COPY pyproject.toml uv.lock ./

# Синхронизируем зависимости прямо в окружение builder
# --frozen требует, чтобы uv.lock был актуальным
RUN uv sync --frozen

# Копируем исходный код
COPY app/ ./app/
COPY my_site/ ./my_site/
COPY manage.py ./
COPY start.sh ./

# Запускаем collectstatic через python, где уже есть все пакеты
RUN ./.venv/bin/python manage.py collectstatic --noinput

# --- Runtime stage ---
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r django && useradd -r -g django django

# Копируем установленные пакеты из builder
# Это даёт минимальный рантайм с теми же зависимостями
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
ENV PATH="/root/.local/bin:/usr/local/bin:$PATH"

# Копируем приложение и статику с правами пользователя
COPY --from=builder --chown=django:django /app/app ./app/
COPY --from=builder --chown=django:django /app/my_site ./my_site/
COPY --from=builder --chown=django:django /app/manage.py ./
COPY --from=builder --chown=django:django /app/staticfiles ./staticfiles/
COPY --from=builder --chown=django:django /app/start.sh ./

RUN chmod +x /app/start.sh

EXPOSE 8000

USER django

CMD ["./start.sh"]
