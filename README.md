# SQL Query Proxy API

REST API для работы с PostgreSQL базой данных: получение метаданных таблиц, схемы и выполнение SQL SELECT запросов.

## Возможности

- **GET /api/tables** - Список всех таблиц БД с пагинацией
- **GET /api/tables/{table_name}/schema** - Детальная схема таблицы (колонки, типы, индексы)
- **POST /api/query** - Выполнение SQL SELECT запросов (только чтение)

## Быстрый старт

### Запуск вручную (локальная разработка)

#### Требования
- Python 3.12+
- PostgreSQL база данных
- uv (установится автоматически)

#### Шаги

1. **Установить зависимости:**
   ```bash
   uv sync
   ```

2. **Настроить окружение:**
   ```bash
   cp .env.example .env
   # Отредактировать .env и указать DATABASE_URL
   ```

   Пример `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/mydb
   ```

3. **Активировать виртуальное окружение:**
   ```bash
   source .venv/bin/activate
   ```

4. **Запустить приложение:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8100
   ```

5. **Доступ к API:**
   - API: http://localhost:8100
   - Swagger UI: http://localhost:8100/docs
   - ReDoc: http://localhost:8100/redoc

### Запуск через Docker (продакшен)

#### Требования
- Docker
- Docker Compose

#### Шаги

1. **Запустить сервисы:**
   ```bash
   docker-compose up -d
   ```

   Это запустит:
   - PostgreSQL базу данных на порту 5432
   - API сервис на порту 8100
   - Автоматически создаст тестовые таблицы из `init.sql`

2. **Проверить логи:**
   ```bash
   docker-compose logs -f api
   ```

3. **Остановить сервисы:**
   ```bash
   docker-compose down
   ```

4. **Остановить и удалить данные:**
   ```bash
   docker-compose down -v
   ```

## API Эндпоинты

### 1. GET /api/tables

Получить список таблиц с пагинацией.

**Query параметры:**
- `page` (int, default=1) - Номер страницы
- `page_size` (int, default=10, max=100) - Элементов на странице

**Пример запроса:**
```bash
curl "http://localhost:8100/api/tables?page=1&page_size=10"
```

**Пример ответа:**
```json
{
  "tables": [
    {
      "table_name": "dict_currencies",
      "table_type": "BASE TABLE",
      "table_size": "40 kB",
      "column_count": 7,
      "table_comment": "Currency reference dictionary"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_count": 2,
    "total_pages": 1
  }
}
```

### 2. GET /api/tables/{table_name}/schema

Получить детальную схему таблицы.

**Path параметры:**
- `table_name` (string) - Имя таблицы

**Пример запроса:**
```bash
curl "http://localhost:8100/api/tables/dict_currencies/schema"
```

**Пример ответа:**
```json
{
  "table_name": "dict_currencies",
  "table_comment": "Currency reference dictionary",
  "column_count": 7,
  "columns": [
    {
      "column_name": "id",
      "data_type": "integer",
      "is_nullable": false,
      "is_primary_key": true,
      "is_foreign_key": false,
      "column_comment": null
    },
    {
      "column_name": "code",
      "data_type": "character varying(3)",
      "is_nullable": false,
      "is_primary_key": false,
      "is_foreign_key": false,
      "column_comment": "ISO 4217 currency code"
    }
  ],
  "indexes": [
    {
      "index_name": "dict_currencies_pkey",
      "columns": ["id"],
      "is_unique": true,
      "is_primary": true
    }
  ]
}
```

### 3. POST /api/query

Выполнить SQL SELECT запрос.

**Request body:**
```json
{
  "query": "SELECT * FROM dict_currencies LIMIT 10"
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8100/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT code, name FROM dict_currencies WHERE is_active = true"}'
```

**Пример ответа:**
```json
{
  "columns": ["code", "name"],
  "rows": [
    ["USD", "US Dollar"],
    ["EUR", "Euro"],
    ["RUB", "Russian Ruble"]
  ],
  "row_count": 3
}
```

**Безопасность:**
- Разрешены только SELECT запросы
- Запрещены: INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE, GRANT, REVOKE
- При попытке использовать запрещенные операции вернется HTTP 400

## Разработка

### Проверка качества кода

После любых изменений в коде обязательно запустить:

```bash
isort . && ruff check --fix . && ruff format . && mypy .
```

Или по отдельности:
```bash
isort .                    # Сортировка импортов
ruff check --fix .         # Линтинг и автофиксы
ruff format .              # Форматирование кода
mypy .                     # Проверка типов
```

### Структура проекта

```
proxy-sql-query/
├── domain/           # Бизнес-сущности и интерфейсы
├── use_cases/        # Прикладная логика
├── infrastructure/   # База данных, конфигурация
├── api/              # FastAPI роуты и схемы
└── main.py           # Точка входа приложения
```

### Архитектура

Проект следует принципам Clean Architecture:

- **Domain Layer** - бизнес-сущности без зависимостей от фреймворков
- **Use Cases Layer** - прикладная бизнес-логика
- **Infrastructure Layer** - реализация работы с БД, настройки
- **API Layer** - FastAPI эндпоинты и Pydantic схемы

### Тесты

Запуск тестов:

```bash
pytest
```

Запуск с покрытием:

```bash
pytest --cov=. --cov-report=html
```

## Конфигурация

Все настройки через переменные окружения (файл `.env`):

```env
# Обязательные
DATABASE_URL=postgresql://user:password@host:5432/database

# Опциональные
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=30.0
API_HOST=0.0.0.0
API_PORT=8100
LOG_LEVEL=INFO
```

## Безопасность

- Только SELECT запросы разрешены
- Валидация SQL через regex с word boundaries
- Connection pooling с таймаутами
- Обработка ошибок без раскрытия внутренних деталей

## Лицензия

MIT
