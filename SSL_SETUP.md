# Создание SSL-сертификатов с помощью Certbot
# Выполнять на хост-машине (не внутри контейнера)

# Создаем директории
mkdir -p certbot nginx_ssl

# Запускаем nginx и certbot
docker-compose up -d nginx certbot

# Получаем сертификат (для каждого домена)
docker-compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    -d tm2d.ru

# Перезапускаем nginx после получения сертификата
docker-compose restart nginx
