from decimal import Decimal

import pytest

from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem


pytestmark = pytest.mark.django_db


def test_create_order_from_cart_creates_items_snapshots_updates_stock_and_clears_cart(auth_client, customer, product):
    cart = Cart.objects.create(user=customer)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    initial_stock = product.stock

    response = auth_client(customer).post(
        "/api/v1/orders/create-from-cart/",
        {"delivery_address": "Moscow, Test street", "phone": "+79990001122", "comment": "Fast delivery"},
        format="json",
    )

    assert response.status_code == 201
    order = Order.objects.get(id=response.data["id"])
    assert order.total_price == Decimal("2000.00")
    assert order.items.count() == 1
    item = order.items.get()
    assert item.product_title_snapshot == product.title
    assert item.product_sku_snapshot == product.sku
    assert item.price_snapshot == product.price
    assert item.subtotal == Decimal("2000.00")

    product.refresh_from_db()
    assert product.stock == initial_stock - 2
    assert not CartItem.objects.filter(cart=cart).exists()


def test_cannot_create_order_from_empty_cart(auth_client, customer):
    response = auth_client(customer).post(
        "/api/v1/orders/create-from-cart/",
        {"delivery_address": "Address", "phone": "+79990001122"},
        format="json",
    )

    assert response.status_code == 400


def test_cannot_create_order_when_stock_is_insufficient(auth_client, customer, product):
    cart = Cart.objects.create(user=customer)
    CartItem.objects.create(cart=cart, product=product, quantity=product.stock + 1)

    response = auth_client(customer).post(
        "/api/v1/orders/create-from-cart/",
        {"delivery_address": "Address", "phone": "+79990001122"},
        format="json",
    )

    assert response.status_code == 400
    assert Order.objects.count() == 0


def test_customer_manager_and_admin_order_visibility(auth_client, customer, other_customer, manager, admin_user):
    own = Order.objects.create(user=customer, total_price=10, delivery_address="Own", phone="+1")
    other = Order.objects.create(user=other_customer, total_price=20, delivery_address="Other", phone="+2")

    customer_response = auth_client(customer).get("/api/v1/orders/")
    assert customer_response.status_code == 200
    assert [item["id"] for item in customer_response.data["results"]] == [own.id]

    manager_response = auth_client(manager).get("/api/v1/orders/")
    assert manager_response.status_code == 200
    assert {item["id"] for item in manager_response.data["results"]} == {own.id, other.id}

    admin_response = auth_client(admin_user).get("/api/v1/orders/")
    assert admin_response.status_code == 200
    assert {item["id"] for item in admin_response.data["results"]} == {own.id, other.id}


def test_customer_can_cancel_created_order_and_stock_is_restored(auth_client, customer, product):
    product.stock = 8
    product.save(update_fields=("stock", "updated_at"))
    order = Order.objects.create(
        user=customer,
        status=Order.Status.CREATED,
        total_price=product.price,
        delivery_address="Address",
        phone="+79990001122",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_title_snapshot=product.title,
        product_sku_snapshot=product.sku,
        price_snapshot=product.price,
        quantity=2,
        subtotal=product.price * 2,
    )

    response = auth_client(customer).post(f"/api/v1/orders/{order.id}/cancel/", {}, format="json")

    assert response.status_code == 200
    assert response.data["status"] == Order.Status.CANCELLED
    product.refresh_from_db()
    assert product.stock == 10


def test_cannot_cancel_completed_order(auth_client, customer, completed_order):
    response = auth_client(customer).post(f"/api/v1/orders/{completed_order.id}/cancel/", {}, format="json")

    assert response.status_code == 400
    completed_order.refresh_from_db()
    assert completed_order.status == Order.Status.COMPLETED


def test_manager_can_update_status_and_customer_cannot(auth_client, customer, manager):
    order = Order.objects.create(
        user=customer,
        status=Order.Status.CREATED,
        total_price=10,
        delivery_address="Address",
        phone="+79990001122",
    )

    customer_response = auth_client(customer).patch(
        f"/api/v1/orders/{order.id}/status/",
        {"status": Order.Status.PROCESSING},
        format="json",
    )
    assert customer_response.status_code == 403

    manager_response = auth_client(manager).patch(
        f"/api/v1/orders/{order.id}/status/",
        {"status": Order.Status.PROCESSING},
        format="json",
    )
    assert manager_response.status_code == 200
    assert manager_response.data["status"] == Order.Status.PROCESSING
