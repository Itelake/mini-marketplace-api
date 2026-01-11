from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import CartItem, Order, OrderItem, User
from app.schemas import OrderResponse
from app.auth import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["Public Orders"]
)

async def get_order_with_items(db: AsyncSession, order_id: int) -> Order:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .where(Order.id == order_id)
    )
    return result.scalar_one()

# ------------------------
# Создать заказ
# ------------------------
@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Берём корзину пользователя
    cart_result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == current_user.id)
    )
    cart_items = cart_result.scalars().all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cart is empty"
        )

    for item in cart_items:
        if item.product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock for one or more products"
            )

    # Списываем количество со склада
    for item in cart_items:
        item.product.quantity -= item.quantity
        db.add(item.product)
        
    # Создаём заказ
    order = Order(user_id=current_user.id, total_price=0)
    db.add(order)
    await db.flush()  # Получаем order.id без commit

    # Создаём элементы заказа и считаем total_price
    order_items = []
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        order_items.append(order_item)
        order.total_price += item.quantity * item.product.price

    db.add_all(order_items)

    # Удаляем корзину
    await db.execute(delete(CartItem).where(CartItem.user_id == current_user.id))

    # Коммитим все изменения одним запросом
    await db.commit()

    # Подгружаем заказ с элементами и продуктами для Pydantic
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
    )
    order_with_items = result.scalar_one()

    return order_with_items

# ------------------------
# Получить мои заказы
# ------------------------
@router.get("/", response_model=list[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .where(Order.user_id == current_user.id)
    )
    return result.scalars().all()

# ------------------------
# Получить конкретный заказ
# ------------------------
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your order"
        )

    return order

# ------------------------
# Оплата заказа
# ------------------------
@router.patch("/{order_id}/pay", response_model=OrderResponse)
async def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your order"
        )

    if order.status != "created":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be paid"
        )

    order.status = "paid"
    await db.commit()
    return await get_order_with_items(db, order.id)

# ------------------------
# Отмена заказа
# ------------------------
@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
            .selectinload(OrderItem.product)
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your order"
        )

    if order.status not in ("created", "paid"):
        raise HTTPException(400, "Order cannot be cancelled")
    
    for item in order.items:
        item.product.quantity += item.quantity

    order.status = "canceled"
    await db.commit()
    return await get_order_with_items(db, order.id)
