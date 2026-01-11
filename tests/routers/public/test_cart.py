import pytest
from httpx import AsyncClient

from app.models import Category, Product

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_cart(authorized_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    category = Category(name="test_category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(
        title="test_product",
        price=100,
        category_id=category.id
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # ---------- Добавить продукт ----------
    response = await authorized_client.post(
        "/public/carts/",
        json={
            "product_id": product.id, 
            "quantity": 2
        }
    )
    assert response.status_code == 201
    item = response.json()
    
    assert item["quantity"] == 2
    assert item["product"]["id"] == product.id

    # ---------- Получить корзину ----------
    response = await authorized_client.get(
        "/public/carts/"
    )
    assert response.status_code == 200
    items = response.json()
    
    assert len(items) == 1
    assert items[0]["quantity"] == 2

    # ---------- Обновить ----------
    response = await authorized_client.patch(
        f"/public/carts/{product.id}",
        json={
            "quantity": 5
        }
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 5

    # ---------- Удалить ----------
    response = await authorized_client.delete(
        f"/public/carts/{product.id}"
    )
    assert response.status_code == 204
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_get_cart_unauthorized(async_client: AsyncClient):
    # ---------- Доступ к корзине без авторизации ----------
    response = await async_client.get("/public/carts/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
    
@pytest.mark.anyio
async def test_add_to_cart_product_not_found(authorized_client: AsyncClient):
    # ---------- Добавление несуществующего продукта в корзину ----------
    response = await authorized_client.post(
        "/public/carts/",
        json={
            "product_id": 10, "quantity": 5
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
    
@pytest.mark.anyio
async def test_delete_item_not_in_cart(authorized_client: AsyncClient):
    # ---------- Удаление продукта, отсутствующего в корзине ----------
    response = await authorized_client.delete(
        "/public/carts/10"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not in cart"