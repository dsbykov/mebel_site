# Сборочный этап
FROM python:3.12-slim AS builder

WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Копируем файлы конфигурации
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --system -r pyproject.toml

# Копируем исходный код
COPY app/ ./app/
COPY my_site/ ./my_site/
COPY manage.py ./

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Финальный этап
FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости для выполнения
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя
RUN groupadd -r django && useradd -r -g django django

# Копируем виртуальное окружение из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем приложение
COPY --from=builder --chown=django:django /app/app ./app/
COPY --from=builder --chown=django:django /app/my_site ./my_site/
COPY --from=builder --chown=django:django /app/manage.py ./
COPY --from=builder --chown=django:django /app/staticfiles ./staticfiles/
COPY --from=builder --chown=django:django /app/media ./media/
COPY --from=builder --chown=django:django /app/.env ./.env

# Экспортируем порт
EXPOSE 8000

# Переключаемся на непривилегированного пользователя
USER django

# Запускаем приложение
CMD ["uvicorn", "app.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
