# Nerjaveyka API

REST API для сайта Nerjaveyka: публичный каталог (категории, кейсы, товары,
услуги, галерея) и приём заявок (обратная связь и контактные запросы).
Администрирование контента — через Django Admin.

## Стек

- Python 3.10+ / Django 5.2
- Django REST Framework, drf-yasg (Swagger/OpenAPI)
- django-filter, поиск и сортировка на уровне API
- SQLite для локальной разработки, PostgreSQL в production
- Gunicorn + WhiteNoise, Docker / Docker Compose
- flake8, black, isort; Prettier для документации и конфигов

## Структура проекта

```text
nerjaveyka/
├── api/                  # общие настройки DRF: пагинация, права, Swagger
├── apps/
│   ├── catalog/          # Category, Case, Product, Service, GalleryItem
│   └── inquiries/        # Feedback, ContactRequest
├── core/                 # settings, urls, wsgi/asgi
├── manage.py
├── requirements.txt      # runtime-зависимости
├── pyproject.toml        # метаданные проекта и конфиги инструментов
├── .flake8               # правила линтера
├── .env.example          # шаблон переменных окружения
├── Dockerfile
├── docker-compose.yml    # web + PostgreSQL
├── DEPLOYMENT.md         # инструкция по развёртыванию
└── db.sqlite3            # локальная база (в git не попадает)
```

## Быстрый старт

Нужен Python 3.10+.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# отредактируйте .env (DJANGO_SECRET_KEY, почта и т.д.)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Приложение будет доступно на <http://127.0.0.1:8000>, админка —
<http://127.0.0.1:8000/admin/>, Swagger —
<http://127.0.0.1:8000/api/v1/swagger/>.

Файл `.env` читается автоматически (python-dotenv). Переменные окружения,
заданные в системе или контейнере, имеют приоритет над `.env`.

## Переменные окружения

Полный список с комментариями — в [`.env.example`](.env.example).

| Переменная                                                                            | Назначение                                             | По умолчанию                     |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------ | -------------------------------- |
| `DJANGO_DEBUG`                                                                        | Режим отладки                                          | `True`                           |
| `DJANGO_SECRET_KEY`                                                                   | Секретный ключ Django; обязателен при `DEBUG=False`    | dev-ключ при `DEBUG=True`        |
| `DJANGO_ALLOWED_HOSTS`                                                                | Хосты через запятую                                    | `localhost,127.0.0.1,testserver` |
| `CSRF_TRUSTED_ORIGINS`                                                                | Доверенные origin'ы для CSRF                           | пусто                            |
| `CORS_ALLOWED_ORIGINS`                                                                | Origin'ы фронтенда для CORS                            | пусто                            |
| `DATABASE_URL`                                                                        | Строка подключения к БД; обязательна при `DEBUG=False` | SQLite `db.sqlite3`              |
| `DJANGO_MEDIA_ROOT`                                                                   | Каталог загруженных файлов                             | `media/`                         |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP для production                                    | console backend при `DEBUG=True` |
| `DEFAULT_FROM_EMAIL`                                                                  | Адрес отправителя                                      | `EMAIL_HOST_USER`                |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`                                   | База для Docker Compose                                | —                                |
| `WEB_PORT`                                                                            | Порт web-контейнера на хосте                           | `8000`                           |
| `GUNICORN_WORKERS`                                                                    | Количество worker'ов Gunicorn                          | `3`                              |

## API

Базовый префикс: `/api/v1/`. Список эндпоинтов также доступен в Swagger.

| Метод | Эндпоинт                 | Описание                 |
| ----- | ------------------------ | ------------------------ |
| GET   | `/health`                | Проверка живости сервиса |
| GET   | `/api/v1/categories/`    | Категории                |
| GET   | `/api/v1/cases/`         | Кейсы                    |
| GET   | `/api/v1/products/`      | Товары                   |
| GET   | `/api/v1/services/`      | Услуги                   |
| GET   | `/api/v1/gallery-items/` | Галерея                  |
| POST  | `/api/v1/feedbacks/`     | Обратная связь           |
| POST  | `/api/v1/requests/`      | Контактная заявка        |
| GET   | `/api/v1/swagger/`       | Swagger UI               |
| GET   | `/api/v1/swagger.json`   | OpenAPI-схема            |

Каталог доступен только для чтения, заявки — только создание.
Пагинация: `?page=2&page_size=20` (максимум 100).
Фильтры: `?category=<id>`, поиск `?search=...`, сортировка
`?ordering=title` / `?ordering=-created_at`.

Пример создания заявки:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/requests/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Иван","phone":"+7 900 000-00-00","email":"ivan@example.com","message":"Нужен расчёт"}'
```

## Тесты и качество кода

```powershell
python manage.py test
python manage.py check

pip install ".[dev]"
flake8 .
black --check .
isort --check-only .
```

Форматирование Markdown/JSON/YAML (Prettier):

```powershell
npm install
npm run format
```

## Docker

```powershell
Copy-Item .env.example .env
# обязательно задайте POSTGRES_PASSWORD и DJANGO_SECRET_KEY
docker compose up --build -d
docker compose logs -f web
```

Контейнер `web` при старте применяет миграции и запускает Gunicorn на порту
`8000`; статика собирается в образ, медиа хранится в volume. Подробности,
ручной деплой, Nginx, обновления и бэкапы — в [DEPLOYMENT.md](DEPLOYMENT.md).
"# nerjaveyka-v1-v2" 
