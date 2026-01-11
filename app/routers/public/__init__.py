from fastapi import APIRouter, Depends

public_router = APIRouter(
    prefix="/public"
)

# подключаем суб-роутеры
from . import order_router, category_router, product_router, auth_router, cart_router

public_router.include_router(order_router.router)
public_router.include_router(product_router.router)
public_router.include_router(auth_router.router)
public_router.include_router(category_router.router)
public_router.include_router(cart_router.router)

