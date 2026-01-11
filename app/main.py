from fastapi import FastAPI

from app.routers.admin import admin_router
from app.routers.public import public_router

app = FastAPI(
    title="Marketplace Backend",
    description="Асинхронный backend для маркетплейса с пользователями, продуктами, корзиной и заказами. "
                "Admin и публичные маршруты, JWT аутентификация, транзакции.",
    version="1.0.0",
)

app.include_router(public_router)
app.include_router(admin_router)