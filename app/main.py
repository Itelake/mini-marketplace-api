from fastapi import FastAPI

from app.routers.admin import admin_router
from app.routers.public import public_router

app = FastAPI(
    title="Mini Marketplace Backend API",
    description=(
        "Асинхронный REST API для мини-маркетплейса. "
        "Поддерживает регистрацию и аутентификацию пользователей, "
        "управление товарами и категориями, корзину и оформление заказов. "
        "Реализованы роли пользователей (user/admin), "
        "JWT-аутентификация, фильтрация и пагинация, "
        "а также административные эндпоинты для управления системой."
    ),
    version="1.0.0",
)

app.include_router(public_router)
app.include_router(admin_router)
