# Развёртывание Nerjaveyka API

Документ описывает production-запуск через Docker Compose и вручную
(Gunicorn + systemd + Nginx). Локальная разработка — в [README.md](README.md).
Для площадки PythonAnywhere используйте отдельную инструкцию —
[PYTHONANYWHERE.md](PYTHONANYWHERE.md).

## 1. Требования

- Сервер с Linux (Ubuntu 22.04+ / Debian 12+), 1 GB RAM и 10 GB диска.
- Docker Engine 24+ и Docker Compose v2 — для контейнерного варианта.
- Python 3.10+ — для ручного варианта.
- Домен и TLS-сертификат (Let's Encrypt) для HTTPS.
- PostgreSQL 14+ (в compose используется `postgres:16-alpine`).

## 2. Подготовка конфигурации

На сервере в каталоге проекта:

```bash
cp .env.example .env

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` содержит секреты: не коммитьте его, ограничьте права (`chmod 600 .env`)
и не передавайте в образ (он исключён через `.dockerignore`).

При `DJANGO_DEBUG=False` приложение намеренно не стартует без
`DJANGO_SECRET_KEY` и `DATABASE_URL` — это защита от небезопасного запуска.

## 3. Запуск через Docker Compose

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f web
```

Что происходит:

1. Поднимается PostgreSQL с healthcheck.
2. Собирается образ: ставятся зависимости и выполняется
   `collectstatic` (WhiteNoise раздаёт статику из образа).
3. `web` ждёт готовности БД, применяет миграции
   (`python manage.py migrate --noinput`) и запускает Gunicorn на `:8000`.
4. Порт публикуется на хост согласно `WEB_PORT` (по умолчанию `8000`).

Проверка:

```bash
curl -fsS http://127.0.0.1:8000/health
# {"status": "ok"}
```

Создание администратора:

```bash
docker compose exec web python manage.py createsuperuser
```

Остановка / обновление:

```bash
docker compose down            # остановить, данные сохраняются в volume
docker compose up --build -d   # пересобрать и перезапустить
docker compose exec web python manage.py migrate   # если миграции не применились автоматически
```

Логи и состояние:

```bash
docker compose logs -f --tail=100 web
docker compose exec web python manage.py check --deploy
```

## 4. Ручной запуск (без Docker)

```bash
python3 -m venv /opt/nerjaveyka/venv
source /opt/nerjaveyka/venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполнить значения

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py check --deploy
```

Проверочный запуск:

```bash
gunicorn core.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
```

### systemd

`/etc/systemd/system/nerjaveyka.service`:

```ini
[Unit]
Description=Nerjaveyka API (Gunicorn)
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/nerjaveyka
EnvironmentFile=/opt/nerjaveyka/.env
ExecStart=/opt/nerjaveyka/venv/bin/gunicorn core.wsgi:application \
    --bind 127.0.0.1:8000 --workers 3 --timeout 60 \
    --access-logfile - --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nerjaveyka
sudo systemctl status nerjaveyka
```

## 5. Nginx и HTTPS

Пример `/etc/nginx/sites-available/nerjaveyka`:

```nginx
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    client_max_body_size 20m;

    location /static/ {
        alias /opt/nerjaveyka/staticfiles/;
        expires 30d;
        access_log off;
    }

    # Только если появятся загружаемые файлы (media/).
    location /media/ {
        alias /opt/nerjaveyka/media/;
        expires 30d;
        access_log off;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/nerjaveyka /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.example.com
```

Важно: `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` уже
настроен, поэтому прокси обязан передавать заголовок `X-Forwarded-Proto`.
При `DEBUG=False` включены `SECURE_SSL_REDIRECT`, HSTS и secure-cookies —
без HTTPS будет редирект или некорректная авторизация.

Для контейнерного варианта Nginx ставится на хост и проксирует на
`127.0.0.1:8000` (или на `WEB_PORT`). Статику можно отдавать как из образа
через WhiteNoise, так и через `alias` на смонтированный каталог.

## 6. Миграции, статика, медиа

```bash
# применить миграции
python manage.py migrate --noinput

# пересобрать статику после изменений (в Docker - пересборка образа)
python manage.py collectstatic --noinput
```

- Статика собирается в `staticfiles/` и раздаётся WhiteNoise при
  `DEBUG=False`; в образе она уже собрана.
- Медиа: `DJANGO_MEDIA_ROOT` (по умолчанию `media/`). В compose подключён
  volume `media_data`. Django не раздаёт медиа при `DEBUG=False` — используйте
  Nginx или объектное хранилище/CDN.
- Модели каталога хранят внешние `image_url`, поэтому загрузка файлов не
  требуется для базовой работы.

## 7. Резервное копирование

PostgreSQL (Docker):

```bash
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  | gzip > "backup-$(date +%F-%H%M).sql.gz"
```

Восстановление:

```bash
gunzip -c backup-2026-10-25-1200.sql.gz \
  | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

SQLite (локальная разработка): достаточно копии файла `db.sqlite3` при
остановленном сервере. Файл `db.sqlite3.before-use` — снимок базы, сделанный
перед первым запуском/миграциями; его можно использовать для отката или
удалить. Резервные копии не коммитятся.

Рекомендуется ежедневный `pg_dump`, хранение копий вне сервера и проверка
восстановления раз в месяц.

## 8. Обновление приложения

```bash
git pull
docker compose build web
docker compose up -d
docker compose exec web python manage.py migrate --noinput
docker compose exec web python manage.py collectstatic --noinput
```

Для ручного варианта: обновить код, `pip install -r requirements.txt`,
`migrate`, `collectstatic`, `systemctl restart nerjaveyka`.

## 9. Чек-лист production

- [ ] `DJANGO_DEBUG=False`
- [ ] Уникальный `DJANGO_SECRET_KEY` (не из примера)
- [ ] `DJANGO_ALLOWED_HOSTS` содержит только реальные домены
- [ ] `CSRF_TRUSTED_ORIGINS` и `CORS_ALLOWED_ORIGINS` ограничены своим фронтендом
- [ ] `DATABASE_URL` с надёжным паролем; PostgreSQL недоступен извне
- [ ] Для PythonAnywhere: `DJANGO_ALLOWED_HOSTS` содержит
      `USERNAME.pythonanywhere.com`, настроены маппинги `/static/` и `/media/`
- [ ] HTTPS + HSTS, сертификат обновляется автоматически
- [ ] `.env` с правами `600`, не попадает в git и образ
- [ ] Настроены бэкапы БД и проверено восстановление
- [ ] `python manage.py check --deploy` не выдаёт ошибок уровня WARNING/ERROR
- [ ] Логи и healthcheck (`/health`) подключены к мониторингу

## 10. Диагностика

| Симптом                                               | Причина / решение                                                    |
| ----------------------------------------------------- | -------------------------------------------------------------------- |
| `ImproperlyConfigured: DJANGO_SECRET_KEY must be set` | Не задан ключ при `DEBUG=False`                                      |
| `ImproperlyConfigured: DATABASE_URL must be set`      | Не задан `DATABASE_URL` при `DEBUG=False`                            |
| `DisallowedHost`                                      | Добавьте домен в `DJANGO_ALLOWED_HOSTS`                              |
| `CSRF verification failed`                            | Проверьте `CSRF_TRUSTED_ORIGINS` и `X-Forwarded-Proto`               |
| Бесконечный редирект на HTTPS                         | Прокси не передаёт `X-Forwarded-Proto: https`                        |
| Админка без стилей                                    | Не выполнен `collectstatic` (в Docker — пересоберите образ)          |
| `web` падает на старте                                | `docker compose logs web`; чаще всего неверный `DATABASE_URL`/пароль |
| 502 от Nginx                                          | Gunicorn не запущен или слушает другой порт                          |
