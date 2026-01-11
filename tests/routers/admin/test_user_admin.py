import pytest
from httpx import AsyncClient

from app.models import User

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_user_admin(admin_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    user_1 = User(
        email="test_user_1@test.com",
        hashed_password="test_password",
        role="admin"
    )
    user_2 = User(
        email="test_user_2@test.com",
        hashed_password="test_password",
        role="admin"
    )
    db_session.add_all([user_1, user_2])
    await db_session.commit()
    await db_session.refresh(user_1)
    await db_session.refresh(user_2)
    
    # ---------- Получение всех пользователей ----------
    response = await admin_client.get(
        "/admin/users/"
    )
    assert response.status_code == 200
    users = response.json()
    
    assert len(users) == 3
    assert all(user["role"] == "admin" for user in users)
    
    # ---------- Обновляем роль пользователю ----------
    response = await admin_client.patch(
        "/admin/users/role",
        json={
            "user_id": user_2.id,
            "role": "user"
        }
    )
    assert response.status_code == 200
    assert response.json()["role"] == "user"
    
    # ---------- Обновляем пароль пользователю ----------
    response = await admin_client.patch(
        "/admin/users/reset-password",
        json={
            "user_id": user_2.id,
            "new_password": "test_new_password"
        }
    )
    assert response.status_code == 200

    # ---------- Логин с НОВЫМ паролем ----------
    response = await admin_client.post(
        "/public/auth/login",
        json={
            "email": user_2.email,
            "password": "test_new_password"
        }
    )
    assert response.status_code == 200

# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_get_users_unauthorized(async_client: AsyncClient):
    # ---------- Получение всех пользователей без авторизации ----------  
    response = await async_client.get(
        "/admin/users/"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
        
@pytest.mark.anyio
async def test_get_users_forbidden(authorized_client: AsyncClient):
    # ---------- Получение всех пользавателей без админских прав ---------- 
    response = await authorized_client.get(
        "/admin/users/"
    )   
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin rights required"

@pytest.mark.anyio
async def test_update_user_not_found(admin_client: AsyncClient):
    # ---------- Обновляем роль пользователя при его отсутствии ----------
    response = await admin_client.patch(
        "/admin/users/role",
        json={
            "user_id": 10,
            "role": "admin"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
    
@pytest.mark.anyio
async def test_reset_password_user_not_found(admin_client: AsyncClient):
    # ---------- Обновляем роль пользователя при его отсутствии ----------
    response = await admin_client.patch(
        "/admin/users/reset-password",
        json={
            "user_id": 10,
            "new_password": "test_new_password"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
    