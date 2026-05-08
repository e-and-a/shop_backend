from decimal import Decimal

import pytest

from apps.catalog.models import Product
from apps.reviews.models import Review


pytestmark = pytest.mark.django_db


def test_category_brand_and_product_lists(api_client, category, brand, product):
    categories = api_client.get("/api/v1/categories/")
    brands = api_client.get("/api/v1/brands/")
    products = api_client.get("/api/v1/products/")

    assert categories.status_code == 200
    assert brands.status_code == 200
    assert products.status_code == 200
    assert categories.data["count"] == 1
    assert brands.data["count"] == 1
    assert products.data["count"] == 1


def test_manager_can_create_category_brand_and_product(auth_client, manager, category, brand):
    client = auth_client(manager)

    category_response = client.post(
        "/api/v1/categories/",
        {"name": "Laptops", "slug": "laptops", "description": "Portable computers"},
        format="json",
    )
    assert category_response.status_code == 201

    brand_response = client.post(
        "/api/v1/brands/",
        {"name": "Lenovo", "slug": "lenovo", "country": "China"},
        format="json",
    )
    assert brand_response.status_code == 201

    product_response = client.post(
        "/api/v1/products/",
        {
            "category": category.id,
            "brand": brand.id,
            "title": "Created Product",
            "slug": "created-product",
            "description": "Created via API",
            "price": "1234.50",
            "stock": 8,
            "sku": "CREATED-1",
            "characteristics": {"battery": "4000mAh"},
            "warranty_months": 12,
            "is_active": True,
        },
        format="json",
    )
    assert product_response.status_code == 201
    assert product_response.data["created_by"] == manager.email


def test_product_soft_delete_sets_is_active_false(auth_client, manager, product):
    client = auth_client(manager)
    response = client.delete(f"/api/v1/products/{product.id}/")

    assert response.status_code == 204
    product.refresh_from_db()
    assert product.is_active is False


def test_anonymous_user_sees_only_active_products(api_client, category, brand, product, manager):
    inactive = Product.objects.create(
        category=category,
        brand=brand,
        title="Inactive",
        slug="inactive",
        description="Hidden",
        price=Decimal("500.00"),
        stock=2,
        sku="INACTIVE-1",
        is_active=False,
        created_by=manager,
    )

    response = api_client.get("/api/v1/products/")
    ids = [item["id"] for item in response.data["results"]]

    assert product.id in ids
    assert inactive.id not in ids


def test_product_filters_search_and_ordering(api_client, category, brand, product, second_product, manager):
    other_category = category.__class__.objects.create(name="Monitors", slug="monitors")
    other_brand = brand.__class__.objects.create(name="Samsung", slug="samsung")
    monitor = Product.objects.create(
        category=other_category,
        brand=other_brand,
        title="Monitor Test",
        slug="monitor-test",
        description="Display search needle",
        price=Decimal("300.00"),
        stock=0,
        sku="MON-NEEDLE",
        is_active=True,
        created_by=manager,
    )

    assert api_client.get(f"/api/v1/products/?category={category.id}").data["count"] == 2
    assert api_client.get(f"/api/v1/products/?brand={brand.id}").data["count"] == 2
    assert api_client.get("/api/v1/products/?min_price=900&max_price=1500").data["count"] == 1
    assert api_client.get("/api/v1/products/?in_stock=false").data["results"][0]["id"] == monitor.id
    assert api_client.get("/api/v1/products/?search=needle").data["results"][0]["sku"] == "MON-NEEDLE"

    ordered_by_price = api_client.get("/api/v1/products/?ordering=price").data["results"]
    assert [item["id"] for item in ordered_by_price] == [monitor.id, product.id, second_product.id]

    ordered_by_stock = api_client.get("/api/v1/products/?ordering=-stock").data["results"]
    assert ordered_by_stock[0]["stock"] >= ordered_by_stock[-1]["stock"]


def test_product_serializer_returns_rating_and_review_count(api_client, product, customer, other_customer):
    Review.objects.create(product=product, user=customer, rating=5, text="Great", is_moderated=True)
    Review.objects.create(product=product, user=other_customer, rating=1, text="Hidden", is_moderated=False)

    response = api_client.get(f"/api/v1/products/{product.id}/")

    assert response.status_code == 200
    assert response.data["average_rating"] == 5.0
    assert response.data["reviews_count"] == 1
