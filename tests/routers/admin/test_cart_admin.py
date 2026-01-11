import pytest
from httpx import AsyncClient

from app.models import CartItem, Category, Product, User

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_cart_admin(admin_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    user_1 = User(
        email="test_user",
        hashed_password="test_password"
    )
    db_session.add(user_1)
    await db_session.commit()
    await db_session.refresh(user_1)
    
    user_2 = User(
        email="test_user_2",
        hashed_password="test_password"
    )
    db_session.add(user_2)
    await db_session.commit()
    await db_session.refresh(user_2)
    
    category = Category(
        name="test_category"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(
        title="test_product",
        price=300,
        category_id=category.id
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
        
    cart_1 = CartItem(
        user_id=user_1.id,
        product_id=product.id,
        quantity=5
    )
    
    db_session.add(cart_1)
    await db_session.commit()
    await db_session.refresh(cart_1)
    
    cart_2 = CartItem(
        user_id=user_2.id,
        product_id=product.id,
        quantity=10
    )
    
    db_session.add(cart_2)
    await db_session.commit()
    await db_session.refresh(cart_2)
    
    # ---------- Получение всех корзин ----------
    response = await admin_client.get(
        "/admin/carts/"
    )
    assert response.status_code == 200
    items = response.json()
    
    assert len(items) == 2
    quantity = {item["quantity"] for item in items}
    assert quantity == {5, 10}
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_cart_admin_forbidden(authorized_client: AsyncClient):
    # ---------- Попытка получить корзину без авторизации ----------
    response = await authorized_client.get(
        "/admin/carts/"
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin rights required"
    
@pytest.mark.anyio
async def test_cart_unauthorized(async_client: AsyncClient):
    # ---------- Попытка получить корзину без админских прав ----------
    response = await async_client.get(
        "/admin/carts/"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
    
    
