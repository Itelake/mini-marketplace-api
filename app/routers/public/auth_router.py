from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import UserAuth, UserResponse, Token
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Public Auth"]
)

# --------------------
# Регистрация
# --------------------
@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED)
async def register_user(
    data: UserAuth,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, что такого email нет
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email is already registered")

    # Создаем пользователя
    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# --------------------
# Логин
# --------------------
@router.post("/login", response_model=Token)
async def login(
    data: UserAuth,
    db: AsyncSession = Depends(get_db)
):
    # Ищем пользователя по email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    # Проверяем пароль
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password")

    # Генерируем токен
    token = create_access_token({"sub": str(user.id)})
    return Token(
    access_token=token,
    token_type="bearer"
)


# --------------------
# Защищённый маршрут: /me
# --------------------
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

