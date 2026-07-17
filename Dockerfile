# --- Builder stage ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем только минимально необходимые инструменты для сборки зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ставим uv и сразу используем его (не нужно venv в билдере)
RUN python -m pip install --upgrade pip && pip install uv
ENV PATH="/root/.local/bin:$PATH"

# Копируем файлы зависимостей раньше кода — чтобы кэш слоёв работал при изменении кода
COPY pyproject.toml uv.lock ./

# Создаём venv и синхронизируем зависимости
RUN uv venv /opt/venv \
    && . /opt/venv/bin/activate \
    && uv sync --frozen

# Копируем исходный код
COPY app/ ./app/
COPY my_site/ ./my_site/
COPY manage.py ./
COPY start.sh ./

# Выполняем collectstatic
RUN python manage.py collectstatic --noinput

# --- Runtime stage ---
FROM python:3.12-slim

WORKDIR /app

# Минимальные рантайм-зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создаём непривилегированного пользователя и группу
RUN groupadd -r django && useradd -r -g django django

# Копируем виртуальное окружение из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем приложение и статику, сразу с правами пользователя
COPY --from=builder --chown=django:django /app/app ./app/
COPY --from=builder --chown=django:django /app/my_site ./my_site/
COPY --from=builder --chown=django:django /app/manage.py ./
COPY --from=builder --chown=django:django /app/staticfiles ./staticfiles/
COPY --from=builder --chown=django:django /app/start.sh ./

RUN chmod +x /app/start.sh

EXPOSE 8000

USER django

CMD ["./start.sh"]
