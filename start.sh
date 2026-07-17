#!/bin/bash
# Скрипт запуска Django приложения
# Применяет миграции перед запуском сервера

set -e

echo "Применение миграций..."
python manage.py migrate --noinput

echo "Сбор статики..."
python manage.py collectstatic --noinput

LOG_DIR="/tmp/logs"
echo "Создание директории логов: $LOG_DIR"
mkdir -p "$LOG_DIR"

echo "Запуск сервера Gunicorn..."
exec gunicorn app.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --log-file "$LOG_DIR/gunicorn.log" \
    --error-logfile "$LOG_DIR/gunicorn_error.log"
