from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.database import get_db
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.models import Product

router = APIRouter(
    prefix="/products", 
    tags=["Admin Products"],
    dependencies=[Depends(require_admin)]
)

# --------------------
# Создать продукт
# --------------------
@router.post(
    "/", 
    response_model=ProductResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    data: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

# --------------------
# Изменить продукт
# --------------------
@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product

# --------------------
# Удалить продукт
# --------------------
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found")

    await db.delete(product)
    await db.commit()
    return
