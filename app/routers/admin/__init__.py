from fastapi import APIRouter, Depends
from app.auth import require_admin

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]
)

# подключаем суб-роутеры
from . import order_router, category_router, product_router, user_router, cart_router

admin_router.include_router(order_router.router)
admin_router.include_router(product_router.router)
admin_router.include_router(user_router.router)
admin_router.include_router(category_router.router)
admin_router.include_router(cart_router.router)
