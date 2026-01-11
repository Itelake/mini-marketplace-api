import pytest
from httpx import AsyncClient

from app.models import Category, Product

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_products(async_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    category = Category(name="test_category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    
    product_1 = Product(
        title="test_product_1",
        price=100,
        category_id=category.id
    )
    
    product_2 = Product(
        title="test_product_2",
        price=200,
        category_id=category.id
    )
    
    db_session.add_all([product_1, product_2])
    await db_session.commit()
    
    # ---------- Получение всех продуктов ----------
    response = await async_client.get(
        "/public/products/"
    )
    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 2
    names = {item["title"] for item in items}
    assert names == {"test_product_1", "test_product_2"}
    
    # ---------- Получение конкретного продукта ----------
    response = await async_client.get(
        f"/public/products/{product_1.id}"
    )
    assert response.status_code == 200
    assert response.json()["title"] == "test_product_1"
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_product_not_found(async_client: AsyncClient):
    # ---------- Получение продукта при его отсутствии ----------
    response = await async_client.get(
        "/public/products/10"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
    