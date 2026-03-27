# Grok Telegram Bot

Telegram-бот на базе xAI/Grok API. Поддерживает текстовый диалог со стримингом, генерацию изображений и видео, анализ фотографий.

## Стек

- **Python 3.12**, aiogram 3
- **PostgreSQL** (pgvector) + SQLAlchemy + Alembic
- **xAI API** (OpenAI-совместимый клиент)
- Docker Compose для деплоя

## Возможности

- Стриминг ответов с live-обновлением сообщения
- Выбор модели через inline-клавиатуру
- `/imagine` / `/imagine pro` — генерация изображений
- `/video` — генерация видео с фоновым поллингом
- Анализ присланных фотографий (vision)
- Контент-модерация перед отправкой запросов
- Rate limiting (10 req/min на пользователя)
- История диалога с мягким сбросом

## Запуск

```bash
cp .env.example .env
# заполнить BOT_TOKEN, XAI_API_KEY, DB_PASSWORD

docker compose up --build -d
```

Бот автоматически применит миграции и запустится в polling-режиме.

## Тесты

```bash
pip install -r dev-requirements.txt
pytest
```

## Структура

```
bot/
  handlers/    — обработчики команд и сообщений
  services/    — LLM, генерация картинок/видео, модерация
  database/    — модели, миграции, middleware сессий
  keyboards/   — inline-клавиатуры
  utils/       — форматирование markdown -> HTML
```
