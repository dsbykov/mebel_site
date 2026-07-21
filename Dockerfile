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
COPY static/ ./static/ 
COPY manage.py ./
COPY start.sh ./


# --- Runtime stage ---
FROM python:3.12-slim

WORKDIR /app

# Копируем виртуальное окружение из builder
COPY --from=builder /app/.venv /app/.venv

# Важно: сказать системе использовать python из venv
ENV PATH="/app/.venv/bin:$PATH"

# Дальше копируй свои файлы и запускай
COPY --from=builder /app/app /app/app
COPY --from=builder /app/my_site /app/my_site
COPY --from=builder /app/manage.py /app/manage.py
COPY --from=builder /app/start.sh /app/start.sh
COPY --from=builder /app/static /app/static

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
