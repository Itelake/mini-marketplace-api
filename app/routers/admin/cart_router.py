from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import CartItem
from app.auth import require_admin
from app.schemas import AdminCartItemResponse

router = APIRouter(
    prefix="/carts", 
    tags=["Admin Carts"],
    dependencies=[Depends(require_admin)]    
)

# --------------------
# Получить все корзины
# --------------------
@router.get("/", response_model=list[AdminCartItemResponse])
async def list_all_carts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem))
    return result.scalars().all()