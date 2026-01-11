from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import hash_password, require_admin
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserRoleUpdate, UserPasswordReset

router = APIRouter(
    prefix="/users",
    tags=["Admin Users"],
    dependencies=[Depends(require_admin)]
)

# --------------------
# Получение всех пользователей
# --------------------
@router.get("/", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

# --------------------
# Обновляем роль пользователю
# --------------------
@router.patch("/role", response_model=UserResponse)
async def update_user_role(
    data: UserRoleUpdate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == data.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found")
    
    user.role = data.role 
    await db.commit()
    await db.refresh(user)
    return user

# --------------------
# Обновляем пароль пользователю
# --------------------
@router.patch("/reset-password", response_model=UserResponse)
async def reset_user_password(
    data: UserPasswordReset,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == data.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Обновляем пароль
    user.hashed_password = hash_password(data.new_password)
    await db.commit()
    await db.refresh(user)
    return user