from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import CartItem, Product, User
from app.schemas import CartItemPayload, CartItemResponse, CartItemUpdate
from app.auth import get_current_user

router = APIRouter(
    prefix="/carts", 
    tags=["Public Carts"]
)

# ------------------------
# Получить корзину
# ------------------------
@router.get("/", response_model=list[CartItemResponse])
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == current_user.id)
    )
    items = result.scalars().all()
    return items

# ------------------------
# Добавить продукт в корзину
# ------------------------
@router.post(
    "/", 
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_to_cart(
    data: CartItemPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )
        
    # Проверяем продукт
    result = await db.execute(
        select(Product).where(Product.id == data.product_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Проверяем, есть ли уже в корзине
    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == current_user.id, CartItem.product_id == data.product_id)
    )
    item = result.scalars().first()

    if item:
        item.quantity += data.quantity
    else:
        item = CartItem(
            user_id=current_user.id,
            product_id=data.product_id,
            quantity=data.quantity
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return item

# ------------------------
# Обновить продукт в корзине
# ------------------------
@router.patch("/{product_id}", response_model=CartItemResponse)
async def update_cart(
    product_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in cart"
        )
        
    if data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    item.quantity = data.quantity
    await db.commit()
    await db.refresh(item)
    return item

# ------------------------
# Удалить продукт с корзины
# ------------------------
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in cart"
        )

    await db.delete(item)
    await db.commit()
    return {"message": "Item removed"}
