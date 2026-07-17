# --- Builder stage ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Минимальные инструменты для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ставим uv в системный PATH (он будет управлять установкой зависимостей)
RUN python -m pip install --upgrade pip && pip install uv
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы зависимостей раньше кода (чтобы кэшировать слой при изменении кода)
COPY pyproject.toml uv.lock ./

# Создаём venv и ставим зависимости через uv, указывая python из venv
RUN uv venv /opt/venv \
    && uv sync --frozen --python /opt/venv/bin/python

# Копируем исходный код
COPY app/ ./app/
COPY my_site/ ./my_site/
COPY manage.py ./
COPY start.sh ./

# ВАЖНО: запускаем collectstatic через python из venv, где уже есть Django
RUN /opt/venv/bin/python manage.py collectstatic


# --- Runtime stage ---
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r django && useradd -r -g django django

# Копируем виртуальное окружение из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

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
