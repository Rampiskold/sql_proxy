# Локальные правила разработки проекта

## Архитектурные принципы

### Чистая архитектура (Clean Architecture)

Проект должен следовать принципам чистой архитектуры с четким разграничением ответственности:

#### Слои приложения

1. **Domain Layer (Домен)**
   - Бизнес-логика и сущности (entities)
   - Не зависит от внешних библиотек и фреймворков
   - Содержит интерфейсы (protocols) для внешних зависимостей
   - Располагается в: `domain/`

2. **Use Cases Layer (Сценарии использования)**
   - Прикладная бизнес-логика
   - Оркестрация взаимодействия между доменом и адаптерами
   - Располагается в: `use_cases/`

3. **Infrastructure Layer (Инфраструктура)**
   - Реализация интерфейсов домена
   - Работа с базами данных, внешними API, файловой системой
   - Располагается в: `infrastructure/`

4. **Presentation Layer (Представление)**
   - API endpoints (FastAPI роуты)
   - DTO (Data Transfer Objects) для входных/выходных данных
   - Валидация запросов
   - Располагается в: `api/`

#### Правила зависимостей

- **Внутренние слои не зависят от внешних**: Domain → Use Cases → Infrastructure/Presentation
- **Инверсия зависимостей**: Infrastructure зависит от абстракций Domain через интерфейсы
- **Dependency Injection**: Все зависимости передаются через конструктор или параметры функций
- **Никакой бизнес-логики в API роутах**: только валидация, вызов use case и формирование ответа

### Структура файлов

```
proxy-sql-query/
├── api/                    # Presentation Layer
│   ├── routes/            # FastAPI роуты
│   ├── schemas/           # Pydantic схемы для запросов/ответов
│   └── dependencies.py    # FastAPI dependencies
├── use_cases/             # Application Layer
│   └── *.py              # Use case классы/функции
├── domain/                # Domain Layer
│   ├── entities/         # Доменные сущности
│   ├── repositories/     # Интерфейсы репозиториев (protocols)
│   └── services/         # Доменные сервисы
├── infrastructure/        # Infrastructure Layer
│   ├── database/         # Реализации репозиториев
│   ├── external/         # Клиенты для внешних API
│   └── config.py         # Конфигурация приложения
├── main.py               # Точка входа приложения
└── pyproject.toml        # Конфигурация проекта
```

## Обязательные проверки кода

### После каждого изменения кода ОБЯЗАТЕЛЬНО запускать:

```bash
# 1. Форматирование с isort
isort .

# 2. Форматирование и автофиксы с ruff
ruff check --fix .
ruff format .

# 3. Проверка типов с mypy
mypy .
```

### Единая команда для всех проверок:

```bash
isort . && ruff check --fix . && ruff format . && mypy .
```

**ВАЖНО**: Код считается готовым только после успешного прохождения всех проверок без ошибок.

## Стиль кодирования

### Общие правила

- **Максимальная длина строки**: 100 символов
- **Строгая типизация**: все функции и методы должны иметь type hints
- **Явное лучше неявного**: избегать магических значений и неочевидного поведения
- **DRY (Don't Repeat Yourself)**: избегать дублирования кода

### Именование

- **Классы**: PascalCase (`UserRepository`, `CreateUserUseCase`)
- **Функции и методы**: snake_case (`get_user_by_id`, `create_user`)
- **Константы**: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`, `DATABASE_URL`)
- **Приватные атрибуты**: начинаются с подчеркивания (`_private_method`)
- **Интерфейсы (Protocols)**: суффикс Protocol (`UserRepositoryProtocol`)

### Type hints

```python
# ✅ Правильно
def get_user(user_id: int) -> User | None:
    ...

async def create_user(data: UserCreateSchema) -> User:
    ...

# ❌ Неправильно
def get_user(user_id):  # отсутствуют type hints
    ...
```

### Dependency Injection

```python
# ✅ Правильно: зависимости через параметры
class CreateUserUseCase:
    def __init__(self, repository: UserRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self, data: UserCreateSchema) -> User:
        return await self._repository.create(data)

# ❌ Неправильно: прямое создание зависимостей
class CreateUserUseCase:
    def __init__(self) -> None:
        self._repository = UserRepository()  # жесткая связь
```

### Разделение ответственности

```python
# ✅ Правильно: роут только валидирует и вызывает use case
@app.post("/users")
async def create_user(
    data: UserCreateSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserResponse:
    user = await use_case.execute(data)
    return UserResponse.from_entity(user)

# ❌ Неправильно: бизнес-логика в роуте
@app.post("/users")
async def create_user(data: UserCreateSchema) -> UserResponse:
    # Валидация email
    if not validate_email(data.email):
        raise ValueError("Invalid email")
    # Создание пользователя
    user = User(email=data.email, name=data.name)
    # Сохранение в БД
    db.save(user)
    return UserResponse.from_entity(user)
```

## Тестирование

- Каждый use case должен быть покрыт unit тестами
- Интеграционные тесты для API endpoints
- Моки для внешних зависимостей в unit тестах
- Минимальное покрытие кода: 80%

## Работа с конфигурацией

- Все настройки через переменные окружения
- Использовать Pydantic Settings для валидации конфигурации
- Никаких хардкодных значений в коде
- Файл `.env` для локальной разработки (не коммитить!)

## Обработка ошибок

- Создавать кастомные исключения для доменных ошибок
- Использовать FastAPI exception handlers для централизованной обработки
- Логировать все ошибки с достаточным контекстом
- Не показывать внутренние ошибки пользователю

## Git workflow

- Коммиты должны быть атомарными и осмысленными
- Префиксы для коммитов: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Перед коммитом обязательно запустить все линтеры
- Pull requests требуют ревью
