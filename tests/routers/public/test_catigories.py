import pytest
from httpx import AsyncClient

from app.models import Category

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_category(async_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    category_1 = Category(name="test_category_1")
    db_session.add(category_1)
    await db_session.commit()
    await db_session.refresh(category_1)
    
    category_2 = Category(name="test_category_2")
    db_session.add(category_2)
    await db_session.commit()
    await db_session.refresh(category_2)


    # ---------- Получаем все категории ----------
    response = await async_client.get("/public/categories/")
    assert response.status_code == 200
    items = response.json()
    
    assert len(items) == 2
    names = {item["name"] for item in items}
    assert names == {"test_category_1", "test_category_2"}

    # ---------- Получаем конкретную категорию ----------
    response = await async_client.get(
        f"/public/categories/{category_1.id}",
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test_category_1"
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_category_not_found(async_client: AsyncClient):
    # ---------- Получение категории при её отсутствии ----------
    response = await async_client.get(
        "/public/categories/10"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

 