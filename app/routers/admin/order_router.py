from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_admin
from app.database import get_db
from app.models import Order, OrderItem
from app.schemas import AdminOrderResponse, OrderUpdateStatus

router = APIRouter(
    prefix="/orders", 
    tags=["Admin Orders"],
    dependencies=[Depends(require_admin)]
)

# --------------------
# Получить все заказы
# --------------------
@router.get("/", response_model=list[AdminOrderResponse])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
    )
    return result.scalars().all()
# --------------------
# Обновить статус заказа
# --------------------
@router.patch("/{order_id}/status", response_model=OrderUpdateStatus)
async def update_status(
    order_id: int,
    payload: OrderUpdateStatus,
    db: AsyncSession = Depends(get_db)
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found")

    order.status = payload.status.value

    await db.commit()
    await db.refresh(order)

    return {"status": order.status}
