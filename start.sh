#!/bin/bash
# Скрипт запуска Django приложения
# Применяет миграции перед запуском сервера

set -e

echo \"Применение миграций...\"
python manage.py migrate --noinput

echo "Запуск сервера Uvicorn..."
exec uvicorn app.asgi:application --host 0.0.0.0 --port 8000
