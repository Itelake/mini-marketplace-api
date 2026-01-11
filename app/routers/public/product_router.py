from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Product
from app.schemas import ProductResponse, ProductFilters

router = APIRouter(
    prefix="/products", 
    tags=["Public Products"]
)

# ------------------------
# Получение всех продуктов
# ------------------------
@router.get("/", response_model=list[ProductResponse])
async def get_products(
    filters: ProductFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    
    if filters.category_id:
        query = query.where(Product.category_id == filters.category_id)
    if filters.min_price is not None:
        query = query.where(Product.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Product.price <= filters.max_price)
        
    query = query.limit(filters.limit).offset(filters.offset)
    
    result = await db.execute(query)
    return result.scalars().all()

# ------------------------
# Получение конкретного продукта
# ------------------------
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found")
    
    return product

