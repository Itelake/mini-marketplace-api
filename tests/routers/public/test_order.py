import pytest
from httpx import AsyncClient

from app.models import CartItem, Order, Product, User

# --------------------------
# Позитивные тесты
# --------------------------
@pytest.mark.anyio
async def test_order(authorized_client: AsyncClient, db_session, user):
    # ---------- Подготовка ----------
    product_1 = Product(title="test_product_1", price=100, quantity=100)
    product_2 = Product(title="test_product_2", price=200, quantity=100)
    db_session.add_all([product_1, product_2])
    await db_session.commit()
    await db_session.refresh(product_1)
    await db_session.refresh(product_2)

    cart_items = [
        CartItem(user_id=user.id, product_id=product_1.id, quantity=5),
        CartItem(user_id=user.id, product_id=product_2.id, quantity=2),
    ]
    db_session.add_all(cart_items)
    await db_session.commit()

    # ---------- Создаём заказ ----------
    response = await authorized_client.post(
        "/public/orders/"
    )
    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "created"
    assert data["total_price"] == 900 
    assert len(data["items"]) == 2
    order_id = data["id"]

    # ---------- Получение заказа ----------
    response = await authorized_client.get(
        "/public/orders/"
    )
    assert response.status_code == 200
    
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    
    # ---------- Получить конкретный заказ ----------
    response = await authorized_client.get(
        f"/public/orders/{order_id}"
    )
    assert response.status_code == 200
    
    order = response.json()
    assert order["id"] == order_id
    assert order["status"] == "created"

    # ---------- Оплата заказа ----------
    response = await authorized_client.patch(
        f"/public/orders/{order_id}/pay"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    
    # ---------- Отмена заказа ----------
    response = await authorized_client.patch(
        f"/public/orders/{order_id}/cancel"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "canceled"
    
# --------------------------
# Негативные тесты
# --------------------------
@pytest.mark.anyio
async def test_create_order_unauthorized(async_client: AsyncClient):
    # ---------- Создание заказа без авторизации ----------
    response = await async_client.post(
        "/public/orders/"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
@pytest.mark.anyio
async def test_pay_order_already_paid(
    authorized_client: AsyncClient,
    db_session, 
    user
):
    # ---------- Подготовка ----------
    order = Order(
        user_id=user.id,
        status="paid",
        total_price=100
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # ---------- Попытка повторной оплаты ----------
    response = await authorized_client.patch(
        f"/public/orders/{order.id}/pay"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Order cannot be paid"

@pytest.mark.anyio
async def test_create_order_cart_empty(authorized_client: AsyncClient):
    # ---------- Создание заказа при пустой корзине ----------
    response = await authorized_client.post(
        "/public/orders/"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"
    
@pytest.mark.anyio
async def test_pay_order_not_found(authorized_client: AsyncClient):
    # ---------- Попытка оплатить несуществующий заказ ----------
    response = await authorized_client.patch(
        "/public/orders/1/pay"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
    
@pytest.mark.anyio
async def test_cancel_not_your_order(authorized_client: AsyncClient, db_session):
    # ---------- Подготовка ----------
    new_user = User(email="test_user",hashed_password="test_password")

    order = Order(
        user_id=new_user.id,
        status="paid",
        total_price=100
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    
    # ---------- Попытка отменить заказ другого пользователя ----------
    response = await authorized_client.patch(
        f"/public/orders/{order.id}/cancel"
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not your order"
    
@pytest.mark.anyio
async def test_create_order_not_enough_stock(
    authorized_client: AsyncClient, 
    db_session, 
    user):
    # ---------- Подготовка ----------
    product_1 = Product(title="test_product_1", price=100, quantity=5)
    db_session.add(product_1)
    await db_session.commit()
    await db_session.refresh(product_1)

    cart_item = [
        CartItem(user_id=user.id, product_id=product_1.id, quantity=10),
    ]
    db_session.add_all(cart_item)
    await db_session.commit()
    
    # ---------- Попытка создать заказ, когда в корзине больше товара, чем на складе  ----------
    response = await authorized_client.post(
        "/public/orders/"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough stock for one or more products"

    

    
    