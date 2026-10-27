"""
WSGI-конфигурация для PythonAnywhere.

Скопируйте этот файл в редактор WSGI на вкладке Web
(путь вида /var/www/USERNAME_pythonanywhere_com_wsgi.py)
и замените его содержимое целиком.

По умолчанию проект ищется в ~/nerjaveyka. Если вы клонировали его
в другой каталог, задайте переменную окружения NERJAVEYKA_PROJECT_DIR
в настройках web-приложения или измените DEFAULT_PROJECT_DIR ниже.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_PROJECT_DIR = Path.home() / 'nerjaveyka'
PROJECT_DIR = Path(
    os.environ.get('NERJAVEYKA_PROJECT_DIR') or DEFAULT_PROJECT_DIR
).expanduser()

if not PROJECT_DIR.is_dir():
    raise RuntimeError(
        f'Каталог проекта не найден: {PROJECT_DIR}. '
        'Исправьте путь в WSGI-файле или задайте NERJAVEYKA_PROJECT_DIR.'
    )

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# На PythonAnywhere приложение всегда работает в production-режиме.
# Значение из .env или панели Web имеет приоритет, потому что setdefault
# не перезаписывает уже заданные переменные окружения.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_DEBUG', 'False')

load_dotenv(PROJECT_DIR / '.env')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
