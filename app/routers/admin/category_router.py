from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth import require_admin
from app.database import get_db
from app.schemas import CategoryCreate, CategoryResponse
from app.models import Category


router = APIRouter(
    prefix="/categories", 
    tags=["Admin Categories"],
    dependencies=[Depends(require_admin)]
)

# ------------------------
# Создать категорию
# ------------------------
@router.post(
    "/", 
    response_model=CategoryResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    category = Category(name=data.name)

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category

# ------------------------
# Обновить категорию
# ------------------------
@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalars().first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Category not found")

    category.name = data.name
    await db.commit()
    await db.refresh(category)

    return category


# ------------------------
# Удалить категорию
# ------------------------
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalars().first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Category not found")

    await db.delete(category)
    await db.commit()

    return {"message": "Category deleted successfully"}