from decimal import Decimal

import pytest

from apps.orders.models import Order, OrderItem


pytestmark = pytest.mark.django_db


def test_admin_stats_endpoint_returns_expected_metrics(auth_client, customer, manager, admin_user, product, second_product):
    completed = Order.objects.create(
        user=customer,
        status=Order.Status.COMPLETED,
        total_price=Decimal("4000.00"),
        delivery_address="Address",
        phone="+79990001122",
    )
    OrderItem.objects.create(
        order=completed,
        product=product,
        product_title_snapshot=product.title,
        product_sku_snapshot=product.sku,
        price_snapshot=product.price,
        quantity=2,
        subtotal=Decimal("2000.00"),
    )
    OrderItem.objects.create(
        order=completed,
        product=second_product,
        product_title_snapshot=second_product.title,
        product_sku_snapshot=second_product.sku,
        price_snapshot=second_product.price,
        quantity=1,
        subtotal=Decimal("2000.00"),
    )
    Order.objects.create(
        user=customer,
        status=Order.Status.CREATED,
        total_price=Decimal("0.00"),
        delivery_address="Address",
        phone="+79990001122",
    )

    admin_response = auth_client(admin_user).get("/api/v1/admin/stats/")

    assert admin_response.status_code == 200
    data = admin_response.data
    assert data["users_count"] == 3
    assert data["customers_count"] == 1
    assert data["managers_count"] == 1
    assert data["products_count"] == 2
    assert data["active_products_count"] == 2
    assert data["orders_count"] == 2
    assert data["orders_by_status"]["COMPLETED"] == 1
    assert data["orders_by_status"]["CREATED"] == 1
    assert data["completed_orders_total"] == Decimal("4000.00")
    assert data["top_products"][0]["quantity_sold"] == 2
    assert len(data["low_stock_products"]) == 2


def test_admin_stats_is_admin_only(auth_client, customer, manager, admin_user):
    assert auth_client(customer).get("/api/v1/admin/stats/").status_code == 403
    assert auth_client(manager).get("/api/v1/admin/stats/").status_code == 403
    assert auth_client(admin_user).get("/api/v1/admin/stats/").status_code == 200
