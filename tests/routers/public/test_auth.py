import pytest
from httpx import AsyncClient

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_login_and_me_success(async_client: AsyncClient):
    # ---------- Регистрация пользователя ----------
    response = await async_client.post(
        "/public/auth/register",
        json={
            "email": "test_user@test.com",
            "password": "test_password"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test_user@test.com"

    # ---------- Логин и получение токена ----------
    response = await async_client.post(
        "/public/auth/login",
        json={
            "email": "test_user@test.com",
            "password": "test_password"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    async_client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    # ---------- Доступ к защищённый маршрут ----------
    response = await async_client.get(
        "/public/auth/me"
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test_user@test.com"   
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_register_duplicate_email(async_client: AsyncClient):
    # ---------- Регистрация с уже существующим email  ----------
    register_data = {"email": "test_user@test.com", "password": "test_password"}
    
    await async_client.post(
        "/public/auth/register", 
        json=register_data
    )

    response = await async_client.post(
        "/public/auth/register", 
        json=register_data
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered"

@pytest.mark.anyio
async def test_login_wrong_password(async_client: AsyncClient):
    # ---------- Логин с неверными учетными данными ----------
    response = await async_client.post(
        "/public/auth/login", 
        json={
            "email": "test_user@test.com",
            "password": "test_password"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

@pytest.mark.anyio
async def test_me_invalid_token(async_client: AsyncClient):
    # ---------- Доступ к /me с невалилным токеном ----------
    response = await async_client.get(
        "/public/auth/me", 
        headers={
            "Authorization": "Bearer invalidtoken"
        }
    )
    assert response.status_code == 401