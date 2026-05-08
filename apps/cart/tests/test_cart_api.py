import pytest

from apps.cart.models import Cart, CartItem


pytestmark = pytest.mark.django_db


def test_customer_gets_own_cart(auth_client, customer):
    response = auth_client(customer).get("/api/v1/cart/")

    assert response.status_code == 200
    assert response.data["items"] == []
    assert response.data["total_price"] == "0.00"


def test_add_product_to_cart_and_repeat_add_increases_quantity(auth_client, customer, product):
    client = auth_client(customer)

    first = client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 2}, format="json")
    second = client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.data["quantity"] == 5
    assert CartItem.objects.get(cart__user=customer, product=product).quantity == 5


def test_cart_rejects_inactive_out_of_stock_and_too_large_quantity(auth_client, customer, product):
    client = auth_client(customer)

    product.is_active = False
    product.save(update_fields=("is_active", "updated_at"))
    inactive = client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
    assert inactive.status_code == 400

    product.is_active = True
    product.stock = 0
    product.save(update_fields=("is_active", "stock", "updated_at"))
    out_of_stock = client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
    assert out_of_stock.status_code == 400

    product.stock = 2
    product.save(update_fields=("stock", "updated_at"))
    too_many = client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")
    assert too_many.status_code == 400


def test_cart_total_is_calculated_by_server(auth_client, customer, product, second_product):
    client = auth_client(customer)
    assert client.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 2}, format="json").status_code == 201
    assert client.post("/api/v1/cart/items/", {"product_id": second_product.id, "quantity": 1}, format="json").status_code == 201

    response = client.get("/api/v1/cart/")

    assert response.status_code == 200
    assert response.data["items_count"] == 3
    assert response.data["total_price"] == "4000.00"


def test_customer_cannot_change_other_users_cart_item(auth_client, customer, other_customer, product):
    other_cart = Cart.objects.create(user=other_customer)
    item = CartItem.objects.create(cart=other_cart, product=product, quantity=1)

    response = auth_client(customer).patch(f"/api/v1/cart/items/{item.id}/", {"quantity": 2}, format="json")

    assert response.status_code == 404
    item.refresh_from_db()
    assert item.quantity == 1


def test_clear_cart_removes_items(auth_client, customer, cart_with_item):
    response = auth_client(customer).delete("/api/v1/cart/clear/")

    assert response.status_code == 204
    assert CartItem.objects.count() == 0
