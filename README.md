# Luminary

Luminary - Python-проект (FastAPI + SQLAlchemy) с архитектурой, ориентированной на модульность и DDD-подход. Исходники находятся в папке `src`, пакет проекта - `luminary`.

## Структура проекта

- `src/` — исходный код проекта
  - `common/` — общие библиотеки (инфраструктура, интерфейсы, реализации сервисов)
  - `luminary/` — основной пакет приложения (assistant, chat, model, source и т.д.)
- `tests/` — юнит и интеграционные тесты

## Требования

**Запуск в Docker:** Docker Engine и Docker Compose.

**Локальная разработка:** Python 3.11+, Poetry.

## Запуск с Docker Compose

1. Клонируйте репозиторий и перейдите в корень проекта (где лежит `docker-compose.yaml`).

2. Создайте внешнюю сеть Docker (в `docker-compose.yaml` она помечена как `external`):

```powershell
docker network create luminary
```

3. Скопируйте пример переменных окружения и при необходимости отредактируйте (ключи API, пароли, порты на хосте):

```powershell
copy .env.example .env
```

4. Поднимите сервисы (образы приложения и миграций соберутся при первом запуске):

```powershell
docker compose up --build
```

Для фонового режима добавьте `-d`:

```powershell
docker compose up --build -d
```

**Что поднимается:** PostgreSQL, RabbitMQ, MinIO (S3), Qdrant, контейнер миграций Alembic, приложение FastAPI (uvicorn на порту **8000** внутри стека) и **nginx** на порту **80** на хосте.
Управление RabbitMQ и консоль MinIO доступны на портах из `.env` (`RABBIT_MANAGEMENT_PORT`, `MINIO_CONSOLE_PORT`).

Остановка:

```powershell
docker compose down
```

Для удаления томов добавьте `-v`:

```powershell
docker compose down -v
```

## Установка (локально)

1. Установите Poetry (если ещё не установлен). Официальная инструкция: https://python-poetry.org/

2. Клонируйте репозиторий и перейдите в папку проекта:

```powershell
git clone <repo-url>
cd luminary
```

3. Установите зависимости и создайте виртуальное окружение через Poetry:

```powershell
poetry install
```

4. Установите git-хуки pre-commit (локально):

```powershell
poetry run pre-commit install
```

Теперь при коммитах будут применяться проверки (линтинг, форматирование и пр.).

## Разработка

- Запуск тестов:

```powershell
poetry run pytest -q
```

или Testing в VSCode.

- Линтеры и форматирование (настройки в `pyproject.toml`):

```powershell
poetry run ruff check src tests
```

## Contributing

Ветки `main` и `dev` защищены и не принимают прямых коммитов. Все изменения вносятся через Pull Request.
Создавайте ветки от `dev`, делайте CI-совместимые коммиты и открывайте PR с описанием изменения и ссылками на связанные задачи/баги.

Основные правила:

- Следуйте gitflow
- Создавайте небольшие логичные изменения по одной задаче
- Соблюдайте существующие правила кодстайла (ruff/black/mypy)
- Добавляйте тесты для новых фич и правок

## Лицензия

MIT
