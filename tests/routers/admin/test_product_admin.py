import pytest
from httpx import AsyncClient

from app.models import Category

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_products_admin(admin_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    category = Category(name="test_category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    
    # ---------- Создание продукта ----------
    response = await admin_client.post(
        "/admin/products/",
        json={
            "title": "test_product",
            "price": 200,
            "category_id": category.id
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "test_product"
    
    product_id = response.json()["id"]
    
    # ---------- Изменение продукта ----------
    response = await admin_client.patch(
        f"/admin/products/{product_id}",
        json={
            "title": "test_product_update"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "test_product_update"
    
    # ---------- Удаления продукта ----------
    response = await admin_client.delete(
        f"/admin/products/{product_id}"
    )
    assert response.status_code == 204

# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_create_product_forbidden(authorized_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    category = Category(name="test_category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    
    # ---------- Попытка создать продукт без прав администратора ----------
    response = await authorized_client.post(
        "/admin/products/",
        json={
            "title": "test_product",
            "price": 200,
            "category_id": category.id
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin rights required"
    
@pytest.mark.anyio
async def test_create_product_unauthorized(async_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    category = Category(name="test_category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    
    # ---------- Попытка создать продукт без авторизации ----------
    response = await async_client.post(
        "/admin/products/",
        json={
            "title": "test_product",
            "price": 200,
            "category_id": category.id
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
@pytest.mark.anyio
async def test_update_product_not_found(admin_client: AsyncClient):
    # ---------- Попытка обновления несуществующего продукта ----------
    response = await admin_client.patch(
        "/admin/products/1",
        json={
            "title": "test_product_update"
        }
    )
    response.status_code == 404
    response.json()["detail"] == "Product not found"
    
@pytest.mark.anyio
async def test_delete_product_not_found(admin_client: AsyncClient):
    # ---------- Попытка удаления несуществующего продукта ----------
    response = await admin_client.delete(
        "/admin/products/1"      
    )
    response.status_code == 404
    response.json()["detail"] == "Product not found"
