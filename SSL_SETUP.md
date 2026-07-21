# SSL-сертификаты на VPS

Все команды выполняются на VPS из `/home/user1/django`.

## Первоначальный выпуск

```sh
mkdir -p certbot/www certbot/conf

docker compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d tm2d.ru -d www.tm2d.ru \
  --deploy-hook "cp -L /etc/letsencrypt/live/tm2d.ru/fullchain.pem /etc/nginx/ssl/fullchain.pem && cp -L /etc/letsencrypt/live/tm2d.ru/privkey.pem /etc/nginx/ssl/privkey.pem"

docker compose up -d
```

Во время первоначального выпуска порт 80 должен обслуживать ACME challenge из
`certbot/www`. Если сертификата ещё нет и nginx из-за этого не запускается,
временно запустите HTTP-only конфигурацию nginx, получите сертификат и верните
основную конфигурацию.

## Автоматическое продление через cron

Certbot сохраняет сертификаты и конфигурацию продления в постоянный каталог
`certbot/conf`. После успешного продления deploy hook копирует новые PEM-файлы
в `nginx_ssl`, откуда их читает nginx.

Используйте в crontab:

```cron
0 3 * * * cd /home/user1/django && docker compose run --rm certbot renew --webroot --webroot-path=/var/www/certbot --deploy-hook "cp -L /etc/letsencrypt/live/tm2d.ru/fullchain.pem /etc/nginx/ssl/fullchain.pem && cp -L /etc/letsencrypt/live/tm2d.ru/privkey.pem /etc/nginx/ssl/privkey.pem" && docker compose exec -T nginx nginx -s reload >> /var/log/certbot-renew.log 2>&1
```

Перезагрузка nginx обязательна: после обновления файлов уже работающий процесс
nginx иначе продолжит использовать загруженный в память старый сертификат.

Проверка без реального выпуска:

```sh
cd /home/user1/django
docker compose run --rm certbot renew --dry-run --webroot --webroot-path=/var/www/certbot \
  --deploy-hook "cp -L /etc/letsencrypt/live/tm2d.ru/fullchain.pem /etc/nginx/ssl/fullchain.pem && cp -L /etc/letsencrypt/live/tm2d.ru/privkey.pem /etc/nginx/ssl/privkey.pem"
docker compose exec -T nginx nginx -t
```
