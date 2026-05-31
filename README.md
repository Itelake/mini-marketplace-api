# 🛒 Mini-Marketplace API (Backend)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)

> Проект создан как pet-project для демонстрации backend-навыков и готов к расширению под реальные бизнес-задачи.

Асинхронный API для интернет-магазина. Проект сфокусирован на правильной архитектуре, безопасности данных и автоматическом тестировании всех бизнес-процессов.

---

## 🚀 Функционал

* **🔐 Auth & Security**: Регистрация и вход через JWT. Реализована ролевая модель: обычный пользователь и администратор.
* **📂 Категории и Товары**: Полноценный каталог с поддержкой категорий. Гибкая фильтрация товаров по цене и принадлежности к категории.
* **🛒 Корзина**: Атомарные операции добавления, изменения количества и удаления товаров.
* **🧾 Заказы**: Логика оформления заказа, сохранение истории покупок и управление статусами (`created` → `paid` → `shipped`).
* **⚙️ Admin API**: Отдельный изолированный интерфейс для менеджеров (управление ассортиментом, категориями и заказами).
* **🧪 Высокое покрытие тестами**: Интеграционные тесты для каждого роута, включая проверку граничных условий и негативных сценариев.
* **🐳 Docker & Docker Compose**: Возможность запуска проекта в контейнерах для быстрого развёртывания и тестирования.

## 🛠 Стек технологий

* **Язык:** Python 3.10+
* **Framework:** FastAPI (Async)
* **ORM:** SQLAlchemy + Alembic (для миграций)
* **БД:** PostgreSQL
* **Контейнеризация:** Docker & Docker Compose
* **Тесты:** Pytest + httpx (для асинхронных запросов)

## 📂 Структура проекта

```text
├── alembic/                # История миграций БД
├── app/
│   ├── routers/            # Маршрутизация API
│   │   ├── admin/          # Эндпоинты управления (защищены правами доступа)
│   │   └── public/         # Публичные эндпоинты (витрина и личный кабинет)
│   ├── auth.py             # Security-слой (JWT, пароли)
│   ├── database.py         # Настройка асинхронного подключения к БД
│   ├── models.py           # Описание таблиц БД (SQLAlchemy)
│   ├── schemas.py          # Модели валидации данных (Pydantic)
│   └── main.py             # Инициализация приложения
├── tests/
│   ├── routers/            # Наборы тестов (Happy Path & Edge Cases)
│   └── conftest.py         # Глобальные фикстуры для тестов
├── docker-compose.yml      # Быстрое развертывание окружения
└── Dockerfile              # Инструкция для сборки образа
```

```bash
# 💻 Установка и запуск

# Клонировать репозиторий
git clone <ВСТАВЬ_СЮДА_ССЫЛКУ_НА_РЕПОЗИТОРИЙ>
cd mini-marketplace

# Создать виртуальное окружение
python -m venv venv

# Активировать окружение
# Linux / MacOS
source venv/bin/activate
# Windows
# venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env

# Применить миграции БД
alembic upgrade head

# Запустить сервер локально
uvicorn app.main:app --reload

# 💻 Запуск через Docker

# Собрать контейнеры
docker-compose up --build -d

# Применить миграции внутри контейнера
docker-compose exec app alembic upgrade head

# Сервер будет доступен на http://localhost:8000
```

## 📖 Документация API
- Swagger UI: http://localhost:8000/docs

## 🔄 Пример бизнес-сценария

1. Пользователь регистрируется и авторизуется
2. Добавляет товары в корзину
3. Оформляет заказ
4. Заказ проходит статусы: created → paid → shipped
5. Администратор управляет статусами заказа через Admin API

## 🔐 Переменные окружения

Проект использует `.env` файл для конфигурации:

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/marketplace
JWT_SECRET_KEY=super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Тестирование

- Интеграционные тесты для всех ключевых эндпоинтов
- Проверка ролей и прав доступа
- Негативные сценарии (401, 403, 404, некорректные данные)
- Изолированная тестовая БД

Запуск тестов:

```bash
pytest -v
```

## ⚠️ Ограничения

- Платежи эмулируются (без реального payment provider)

- Нет внешних интеграций

- Логика доставки не реализована

## 🛣 Roadmap

- [ ] Интеграция платежного провайдера (Stripe / YooKassa)
- [ ] Redis для кеширования и rate-limit
- [ ] Celery / Background Tasks для email-уведомлений
- [ ] CI (GitHub Actions) + coverage report
- [ ] OpenAPI examples для всех эндпоинтов

## 📄 Лицензия

MIT License © 
