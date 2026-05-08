from decimal import Decimal

import pytest

from apps.orders.models import Order


pytestmark = pytest.mark.django_db


def product_payload(category, brand, suffix="new"):
    return {
        "category": category.id,
        "brand": brand.id,
        "title": f"Managed Product {suffix}",
        "slug": f"managed-product-{suffix}",
        "description": "Managed description",
        "price": "1500.00",
        "stock": 4,
        "sku": f"MANAGED-{suffix}",
        "characteristics": {"ram": "16GB"},
        "warranty_months": 12,
        "is_active": True,
    }


def test_catalog_read_is_public_but_write_requires_manager_or_admin(api_client, auth_client, customer, manager, category, brand, product):
    assert api_client.get("/api/v1/products/").status_code == 200
    assert api_client.post("/api/v1/products/", product_payload(category, brand, "anon"), format="json").status_code in {401, 403}

    customer_client = auth_client(customer)
    assert customer_client.post("/api/v1/products/", product_payload(category, brand, "customer"), format="json").status_code == 403

    manager_client = auth_client(manager)
    create = manager_client.post("/api/v1/products/", product_payload(category, brand, "manager"), format="json")
    assert create.status_code == 201
    update = manager_client.patch(f"/api/v1/products/{create.data['id']}/", {"stock": 9}, format="json")
    assert update.status_code == 200
    assert update.data["stock"] == 9


def test_admin_has_full_catalog_access(api_client, auth_client, admin_user, category, brand):
    client = auth_client(admin_user)
    created = client.post("/api/v1/categories/", {"name": "Admin Cat", "slug": "admin-cat"}, format="json")
    assert created.status_code == 201
    deleted = client.delete(f"/api/v1/categories/{created.data['id']}/")
    assert deleted.status_code == 204

    brand_response = client.post(
        "/api/v1/brands/",
        {"name": "Admin Brand", "slug": "admin-brand", "country": "EU"},
        format="json",
    )
    assert brand_response.status_code == 201


def test_order_permissions_and_admin_stats(api_client, auth_client, customer, other_customer, manager, admin_user):
    own_order = Order.objects.create(
        user=customer,
        status=Order.Status.CREATED,
        total_price=Decimal("10.00"),
        delivery_address="Own",
        phone="+79990000001",
    )
    other_order = Order.objects.create(
        user=other_customer,
        status=Order.Status.CREATED,
        total_price=Decimal("20.00"),
        delivery_address="Other",
        phone="+79990000002",
    )

    customer_client = auth_client(customer)
    assert customer_client.get(f"/api/v1/orders/{own_order.id}/").status_code == 200
    assert customer_client.get(f"/api/v1/orders/{other_order.id}/").status_code == 404
    assert customer_client.patch(f"/api/v1/orders/{own_order.id}/status/", {"status": "PROCESSING"}, format="json").status_code == 403
    assert customer_client.get("/api/v1/admin/stats/").status_code == 403

    manager_client = auth_client(manager)
    status_response = manager_client.patch(
        f"/api/v1/orders/{own_order.id}/status/",
        {"status": "PROCESSING"},
        format="json",
    )
    assert status_response.status_code == 200
    assert status_response.data["status"] == "PROCESSING"
    assert manager_client.get("/api/v1/admin/stats/").status_code == 403

    admin_client = auth_client(admin_user)
    stats = admin_client.get("/api/v1/admin/stats/")
    assert stats.status_code == 200
    assert stats.data["orders_count"] == 2

    assert api_client.get("/api/v1/admin/stats/").status_code in {401, 403}
