import pytest
from httpx import AsyncClient

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_category_admin(admin_client: AsyncClient):
    # ---------- Создание категории ----------
    response = await admin_client.post(
        "/admin/categories/",
        json={
            "name": "test_category"
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "test_category"
    
    category_id = response.json()["id"]
    
    # ---------- Обновление категории ----------
    response = await admin_client.patch(
        f"/admin/categories/{category_id}",
        json={
            "name": "test_category_update"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test_category_update"
    
    # ---------- Удаление категории ----------
    response = await admin_client.delete(
        f"/admin/categories/{category_id}"
    )
    assert response.status_code == 204
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_create_category_forbidden(authorized_client: AsyncClient):
    # ---------- Попытка создать категорию без админских прав ----------
    response = await authorized_client.post(
        "/admin/categories/",
        json={
            "name": "test_product"
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin rights required"
    
@pytest.mark.anyio
async def test_create_category_unauthorized(async_client: AsyncClient):
    # ---------- Попытка создать продукт без авторизации  ----------
    response = await async_client.post(
        "/admin/categories/",
        json={
            "name": "test_product"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
@pytest.mark.anyio
async def test_update_category_not_found(admin_client: AsyncClient):
    # ---------- Попытка обновления несуществующей категории ----------
    response = await admin_client.patch(
        "/admin/categories/1",
        json={
            "name": "test_product_update"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
    
@pytest.mark.anyio
async def test_delete_product_not_found(admin_client: AsyncClient):
    # ---------- Попытка удаления несуществующей категории ----------
    response = await admin_client.delete(
        "/admin/categories/1"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


