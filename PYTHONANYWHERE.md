# Деплой Nerjaveyka API на PythonAnywhere

Инструкция для площадки [PythonAnywhere](https://www.pythonanywhere.com/).
Для VPS/Docker см. [DEPLOYMENT.md](DEPLOYMENT.md).

Проект использует Django 5.2, поэтому на PythonAnywhere выбирайте
**Python 3.10–3.13** (рекомендуется 3.13). Python 3.14 для Django 5.2
официально не поддерживается.

## 1. Подготовить и запушить код

Локально проверьте, что секреты и база не попадают в git:

```bash
git status
git add .
git commit -m "Prepare deployment for PythonAnywhere"
git push origin main
```

`.env`, `db.sqlite3`, `venv/`, `staticfiles/`, `media/` и `__pycache__/`
должны оставаться вне репозитория. Они уже перечислены в `.gitignore`.

## 2. Клонировать проект на PythonAnywhere

Откройте **Consoles → Bash** и выполните:

```bash
cd ~
git clone https://github.com/dawwud07/nerjaveyka-v1-v2.git nerjaveyka
cd nerjaveyka
```

Если проект уже склонирован, обновите его:

```bash
cd ~/nerjaveyka
git pull
```

Для приватного репозитория настройте SSH-ключ PythonAnywhere в GitHub
или используйте personal access token вместо пароля.

## 3. Создать виртуальное окружение

В той же Bash-консоли:

```bash
mkvirtualenv --python=/usr/bin/python3.13 nerjaveyka-venv
workon nerjaveyka-venv
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Если версии 3.13 на площадке нет, посмотрите доступные интерпретаторы:

```bash
ls /usr/bin/python3.*
```

и создайте окружение с подходящей версией (3.10–3.13). При повторном
входе в консоль окружение активируется командой `workon nerjaveyka-venv`.

## 4. Создать `.env`

```bash
cd ~/nerjaveyka
cp deploy/pythonanywhere/.env.example .env
nano .env
chmod 600 .env
```

Обязательно замените:

- `YOUR_USERNAME` — на имя вашего аккаунта PythonAnywhere;
- `DJANGO_SECRET_KEY` — на новый ключ;
- `DATABASE_URL` — если используете не SQLite.

Сгенерировать секретный ключ:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Для бесплатного аккаунта домен будет вида
`USERNAME.pythonanywhere.com`, поэтому в `.env` должны быть:

```dotenv
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=USERNAME.pythonanywhere.com,www.USERNAME.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://USERNAME.pythonanywhere.com,https://www.USERNAME.pythonanywhere.com
```

Если фронтенд при разработке открыт на `http://localhost:3000`, добавьте
его origin в `.env` (без слэша на конце):

```dotenv
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

После изменения `.env` нажмите **Reload** на вкладке **Web**.

### База данных

По умолчанию в шаблоне используется SQLite:

```dotenv
DATABASE_URL=sqlite:////home/USERNAME/nerjaveyka/db.sqlite3
```

Обратите внимание на **четыре** слэша после `sqlite:` — путь должен быть
абсолютным. Для небольшого сайта SQLite подходит, но при интенсивной
записи возможны блокировки (`database is locked`).

MySQL на PythonAnywhere доступен на платных тарифах и на бесплатных
аккаунтах, созданных до 15 января 2026 года. На новом бесплатном аккаунте
используйте SQLite.

Если нужен MySQL PythonAnywhere:

1. Создайте базу на вкладке **Databases** и запомните пароль.
2. Установите драйвер в виртуальном окружении:

   ```bash
   workon nerjaveyka-venv
   pip install mysqlclient
   ```

3. Укажите строку подключения в `.env` (обратите внимание на кавычки
   вокруг значения из-за символа `$`):

   ```dotenv
   DATABASE_URL='mysql://USERNAME:DB_PASSWORD@USERNAME.mysql.pythonanywhere-services.com/USERNAME$nerjaveyka'
   ```

PostgreSQL на PythonAnywhere не предоставляется; `psycopg` в
`requirements.txt` нужен для Docker/VPS-варианта.

## 5. Применить миграции и собрать статику

```bash
workon nerjaveyka-venv
cd ~/nerjaveyka
mkdir -p media

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py check --deploy
```

`check --deploy` не должен показывать ошибки. Предупреждения о HSTS или
secure-cookies при `DJANGO_DEBUG=False` означают, что `.env` не загрузился.

## 6. Создать web-приложение

На вкладке **Web**:

1. **Add a new web app** → **Manual configuration** (не «Django»).
2. Выберите ту же версию Python, что и для virtualenv (например, 3.13).
3. В разделе **Virtualenv** укажите `nerjaveyka-venv` — площадка дополнит
   путь до `/home/USERNAME/.virtualenvs/nerjaveyka-venv`.
4. В разделе **Code** укажите:
   - **Source code**: `/home/USERNAME/nerjaveyka`
   - **Working directory**: `/home/USERNAME/nerjaveyka`

## 7. Настроить WSGI-файл

На вкладке **Web** нажмите ссылку на WSGI-файл
(`/var/www/USERNAME_pythonanywhere_com_wsgi.py`) и замените его
содержимое целиком на содержимое файла
[`deploy/pythonanywhere/wsgi.py`](deploy/pythonanywhere/wsgi.py).

WSGI-файл сам:

- добавляет `~/nerjaveyka` в `sys.path`;
- выставляет `DJANGO_DEBUG=False`;
- загружает `.env` до импорта Django;
- создаёт `application` для PythonAnywhere.

Если проект лежит не в `~/nerjaveyka`, измените `DEFAULT_PROJECT_DIR`
в WSGI-файле или задайте переменную `NERJAVEYKA_PROJECT_DIR` в настройках
web-приложения.

Сохраните файл и нажмите **Reload**.

## 8. Настроить статические файлы

На вкладке **Web** в разделе **Static files** добавьте два маппинга:

| URL      | Directory                              |
| -------- | -------------------------------------- |
| `/static/` | `/home/USERNAME/nerjaveyka/staticfiles` |
| `/media/`  | `/home/USERNAME/nerjaveyka/media`       |

После изменения маппингов обязательно нажмите **Reload**. Статику
нужно пересобирать после каждого обновления кода:

```bash
python manage.py collectstatic --noinput
```

## 9. Проверить сайт

Откройте:

- `https://USERNAME.pythonanywhere.com/health` — должно вернуться
  `{"status": "ok"}`;
- `https://USERNAME.pythonanywhere.com/admin/` — админка со стилями;
- `https://USERNAME.pythonanywhere.com/api/v1/swagger/` — Swagger UI.

Если сайт не открывается, откройте ссылку **Error log** на вкладке
**Web** — там будет traceback.

## 10. Обновление приложения

После `git push` локально:

```bash
cd ~/nerjaveyka
workon nerjaveyka-venv
git pull
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
```

Затем нажмите **Reload** на вкладке **Web**. Перезапуск Python-процесса
не применяет изменения автоматически.

## 11. Резервная копия SQLite

Скопируйте базу в домашний каталог (не в git):

```bash
cd ~/nerjaveyka
cp db.sqlite3 ~/nerjaveyka-backup-$(date +%F-%H%M).sqlite3
```

Для MySQL используйте `mysqldump` (команда доступна на вкладке
**Databases**). Храните копии вне проекта и периодически проверяйте
восстановление.

## 12. Частые ошибки

| Симптом | Решение |
| --- | --- |
| `DisallowedHost` / `400 Bad Request` | Добавьте точный домен в `DJANGO_ALLOWED_HOSTS`, сохраните `.env` и нажмите **Reload**. |
| `ImproperlyConfigured: DJANGO_SECRET_KEY must be set` | `.env` не найден или не загрузился. Проверьте путь `~/nerjaveyka/.env` и WSGI-файл. |
| `ImproperlyConfigured: DATABASE_URL must be set` | При `DJANGO_DEBUG=False` нужен `DATABASE_URL`; проверьте строку SQLite/MySQL. |
| `ModuleNotFoundError: No module named 'core'` | В WSGI-файле неверный `PROJECT_DIR` или в Web-вкладке указан не тот virtualenv. |
| Админка без CSS, `/static/...` отдаёт 404 | Не выполнен `collectstatic` или не настроен маппинг `/static/` → `staticfiles`. |
| `CSRF verification failed` | Проверьте `CSRF_TRUSTED_ORIGINS` (со схемой `https://`) и что сайт открыт по HTTPS. |
| `CORS policy: No 'Access-Control-Allow-Origin'` | Добавьте origin фронтенда в `CORS_ALLOWED_ORIGINS` (без слэша на конце), например `http://localhost:3000`, и нажмите **Reload**. |
| Бесконечный редирект на HTTPS | Временно задайте `DJANGO_SECURE_SSL_REDIRECT=False` в `.env`, проверьте заголовок `X-Forwarded-Proto` и настройки прокси. |
| `database is locked` | SQLite не любит параллельную запись; перейдите на MySQL. |
| `No module named 'MySQLdb'` | Установите `mysqlclient` в активированное виртуальное окружение. |
| Изменения не применились | Нажмите **Reload**; для статики дополнительно выполните `collectstatic`. |

## Особенности бесплатного аккаунта

- Доступен только домен `USERNAME.pythonanywhere.com`; свой домен — на
  платном тарифе.
- Ограничены CPU-секунды и дисковое пространство, поэтому SQLite и
  небольшой каталог подходят лучше всего.
- Исходящие запросы и SMTP могут быть ограничены; для production-почты
  используйте разрешённый почтовый сервис.
- `DEBUG=False` обязателен: не публикуйте сайт с отладочной страницей
  и dev-секретом.
