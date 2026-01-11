import pytest
from httpx import AsyncClient

from app.models import Order, OrderItem, Product, User

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_order_admin(admin_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    user = User(
        email="test_user_1@test.com",
        hashed_password="test_password",
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product_1 = Product(
        title="test_product",
        price=100
    )
    
    product_2 = Product(
        title="test_product",
        price=500
    )
    db_session.add_all([product_1, product_2])
    await db_session.commit()
    await db_session.refresh(product_1)
    await db_session.refresh(product_2)

    order = Order(
        user_id=user.id,
        total_price=2700,
        items=[
            OrderItem(
                product_id=product_1.id,
                quantity=2,
                price=product_1.price
            ),
            OrderItem(
                product_id=product_2.id,
                quantity=5,
                price=product_2.price
            )
        ]
    )

    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # ---------- Получение всех заказов ----------
    response = await admin_client.get(
        "/admin/orders/"
    )
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1

    items = orders[0]["items"]
    quantities = {item["quantity"] for item in items}

    assert quantities == {2, 5}
    
    # ---------- Обновление статуса заказа ----------
    response = await admin_client.patch(
        f"/admin/orders/{order.id}/status",
        json={
            "status": "paid"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"
     
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_get_order_forbidden(authorized_client: AsyncClient):
    # ---------- Попытка получить заказы без админских прав ----------
    response = await authorized_client.get(
        "/admin/orders/"
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin rights required"
    
@pytest.mark.anyio
async def test_get_order_unauthorized(async_client: AsyncClient):
    # ---------- Попытка получить заказы без авторизации  ----------
    response = await async_client.get(
        "/admin/orders/"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
@pytest.mark.anyio
async def test_patch_order_not_found(admin_client):
    response = await admin_client.patch(
        "/admin/orders/10/status",
        json={
            "status": "paid"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    
