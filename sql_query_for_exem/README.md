# 🛠️ SQL Agent Tools

Набор инструментов для работы с PostgreSQL базой данных через FastAPI.

## 📦 Инструменты

### 1. SQLDatabaseGetTablesTool
**Файл:** `sql_database_get_tables.py`

**Назначение:** Получение списка всех таблиц в базе данных с метаданными

**Параметры:**
- `reasoning` (str) - Почему нужен список таблиц
- `page` (int) - Номер страницы (default: 1)
- `page_size` (int) - Размер страницы (default: 10, max: 100)

**Возвращает:**
```json
{
  "tables": [
    {
      "table_name": "dict_currencies",
      "table_type": "BASE TABLE",
      "table_size": "40 kB",
      "column_count": 7,
      "table_comment": "Справочник валют"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_count": 8,
    "total_pages": 1
  }
}
```

**Когда использовать:**
- Нужно узнать какие таблицы есть в БД
- Поиск таблицы по названию или описанию
- Получение обзора структуры БД

---

### 2. SQLTableGetSchemaTool
**Файл:** `sql_table_get_schema.py`

**Назначение:** Получение детальной схемы конкретной таблицы

**Параметры:**
- `reasoning` (str) - Зачем нужна схема этой таблицы
- `table_name` (str) - Точное название таблицы

**Возвращает:**
```json
{
  "summary": {
    "table_name": "dict_currencies",
    "table_comment": "Справочник валют",
    "total_columns": 7,
    "has_primary_key": true,
    "has_foreign_keys": false
  },
  "columns_by_type": {
    "integer": ["id"],
    "character varying": ["code", "name", "symbol"]
  },
  "full_schema": {
    "columns": [...],
    "indexes": [...]
  }
}
```

**Когда использовать:**
- Перед написанием SQL запроса
- Нужно узнать какие колонки есть в таблице
- Проверка типов данных для WHERE условий
- Поиск Primary Key для JOIN

---

### 3. SQLDatabaseExecuteQueryTool
**Файл:** `sql_database_execute_query.py`

**Назначение:** Выполнение SQL SELECT запросов

**Параметры:**
- `reasoning` (str) - Зачем нужен этот запрос
- `sql_query` (str) - SQL SELECT запрос
- `expected_columns` (list[str]) - Ожидаемые колонки (optional)

**Возвращает:**
```json
{
  "summary": {
    "row_count": 3,
    "column_count": 7,
    "columns": ["id", "code", "name", "symbol", "is_active", "created_at", "updated_at"],
    "has_data": true
  },
  "data": {
    "columns": [...],
    "rows": [...]
  }
}
```

**Ограничения безопасности:**
- ✅ Разрешены: SELECT запросы
- ❌ Запрещены: INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE

**Когда использовать:**
- Получение данных из таблицы
- Аналитические запросы с агрегацией
- JOIN между таблицами
- Фильтрация и сортировка данных

---

## 🔄 Типичный workflow

### Сценарий 1: Исследование новой БД

```python
# 1. Получить список таблиц
SQLDatabaseGetTablesTool(
    reasoning="Нужно понять какие таблицы есть в БД для начала работы",
    page=1,
    page_size=20
)

# 2. Изучить схему интересующей таблицы
SQLTableGetSchemaTool(
    reasoning="Нужно понять структуру таблицы dict_currencies перед запросом данных",
    table_name="dict_currencies"
)

# 3. Выполнить запрос
SQLDatabaseExecuteQueryTool(
    reasoning="Получить список всех активных валют для анализа",
    sql_query="SELECT * FROM dict_currencies WHERE is_active = true LIMIT 10"
)
```

### Сценарий 2: Аналитический запрос

```python
# 1. Найти нужные таблицы
SQLDatabaseGetTablesTool(
    reasoning="Ищу таблицы связанные с бюджетом",
    page=1,
    page_size=10
)

# 2. Изучить схемы для JOIN
SQLTableGetSchemaTool(
    reasoning="Нужны Primary/Foreign Keys для JOIN между budget_actuals и dict_tribes",
    table_name="budget_actuals"
)

SQLTableGetSchemaTool(
    reasoning="Проверяю структуру dict_tribes для JOIN",
    table_name="dict_tribes"
)

# 3. Выполнить аналитический запрос
SQLDatabaseExecuteQueryTool(
    reasoning="Посчитать количество бюджетных записей по трайбам",
    sql_query="""
        SELECT 
            dt.tribe_name, 
            COUNT(ba.id) as budget_count,
            SUM(ba.amount) as total_amount
        FROM dict_tribes dt
        LEFT JOIN budget_actuals ba ON dt.id = ba.tribe_id
        GROUP BY dt.tribe_name
        ORDER BY budget_count DESC
    """,
    expected_columns=["tribe_name", "budget_count", "total_amount"]
)
```

### Сценарий 3: Поиск данных по условию

```python
# 1. Изучить схему для правильного WHERE
SQLTableGetSchemaTool(
    reasoning="Нужно узнать тип данных колонки log_level и created_at для фильтрации",
    table_name="app_logs"
)

# 2. Выполнить запрос с фильтрацией
SQLDatabaseExecuteQueryTool(
    reasoning="Найти все ERROR логи за последний день",
    sql_query="""
        SELECT * 
        FROM app_logs 
        WHERE log_level = 'ERROR' 
          AND created_at > NOW() - INTERVAL '1 day'
        ORDER BY created_at DESC
        LIMIT 50
    """,
    expected_columns=["id", "created_at", "log_level", "message"]
)
```

---

## 💡 Best Practices

### 1. Всегда используйте reasoning
```python
# ❌ Плохо
reasoning="нужны данные"

# ✅ Хорошо
reasoning="Нужно получить список валют для проверки наличия USD перед конвертацией бюджета"
```

### 2. Ограничивайте результаты
```python
# ❌ Плохо
sql_query="SELECT * FROM app_logs"  # Может вернуть миллионы строк

# ✅ Хорошо
sql_query="SELECT * FROM app_logs ORDER BY created_at DESC LIMIT 100"
```

### 3. Изучайте схему перед запросом
```python
# ❌ Плохо - сразу запрос без знания структуры
SQLDatabaseExecuteQueryTool(
    sql_query="SELECT name, price FROM products"  # Может не быть таких колонок
)

# ✅ Хорошо - сначала схема
SQLTableGetSchemaTool(table_name="products")
# Потом запрос с правильными колонками
```

### 4. Используйте expected_columns
```python
# ✅ Хорошо - валидация результата
SQLDatabaseExecuteQueryTool(
    sql_query="SELECT id, name, price FROM products",
    expected_columns=["id", "name", "price"]
)
```

### 5. Обрабатывайте ошибки
```python
# Инструмент вернет JSON с error полем при ошибке
result = await tool()
if "error" in result:
    # Обработать ошибку
    # Посмотреть hints для решения
```

---

## 🔒 Безопасность

### Разрешенные операции
- ✅ SELECT
- ✅ WITH (CTE)
- ✅ JOIN, UNION
- ✅ Агрегатные функции (COUNT, SUM, AVG, etc.)
- ✅ Подзапросы

### Запрещенные операции
- ❌ INSERT
- ❌ UPDATE
- ❌ DELETE
- ❌ DROP
- ❌ TRUNCATE
- ❌ ALTER
- ❌ CREATE

При попытке выполнить запрещенную операцию вернется ошибка:
```json
{
  "error": "Query contains forbidden keyword: delete"
}
```

---

## 🚀 Примеры SQL запросов

### Простой SELECT
```sql
SELECT * FROM dict_currencies LIMIT 10;
```

### Фильтрация
```sql
SELECT * FROM app_logs 
WHERE log_level = 'ERROR' 
  AND created_at > '2024-01-01'
ORDER BY created_at DESC
LIMIT 50;
```

### Агрегация
```sql
SELECT 
    log_level, 
    COUNT(*) as count,
    DATE(created_at) as date
FROM app_logs
GROUP BY log_level, DATE(created_at)
ORDER BY date DESC, count DESC;
```

### JOIN
```sql
SELECT 
    dt.tribe_name,
    ba.amount,
    ba.created_at
FROM budget_actuals ba
INNER JOIN dict_tribes dt ON ba.tribe_id = dt.id
WHERE ba.amount > 100000
ORDER BY ba.amount DESC
LIMIT 20;
```

### CTE (Common Table Expression)
```sql
WITH tribe_stats AS (
    SELECT 
        tribe_id,
        COUNT(*) as record_count,
        SUM(amount) as total_amount
    FROM budget_actuals
    GROUP BY tribe_id
)
SELECT 
    dt.tribe_name,
    ts.record_count,
    ts.total_amount
FROM tribe_stats ts
JOIN dict_tribes dt ON ts.tribe_id = dt.id
ORDER BY ts.total_amount DESC;
```

---

## 📝 Регистрация инструментов

Инструменты автоматически регистрируются через `ToolRegistryMixin` при импорте:

```python
from sgr_agent_core.tools.sql_agent import (
    SQLDatabaseGetTablesTool,
    SQLTableGetSchemaTool,
    SQLDatabaseExecuteQueryTool,
)
```

---

## 🔧 Конфигурация

API URL по умолчанию: `http://localhost:18790`

Для изменения URL отредактируйте соответствующие файлы инструментов.

---

## 📊 API Endpoints

Инструменты используют следующие эндпоинты:

1. `GET /api/tables?page={page}&page_size={page_size}` - список таблиц
2. `GET /api/tables/{table_name}/schema` - схема таблицы
3. `POST /api/query` - выполнение SQL запроса

Подробнее см. документацию API.
