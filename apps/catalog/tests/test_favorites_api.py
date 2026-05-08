import pytest

from apps.catalog.models import Favorite


pytestmark = pytest.mark.django_db


def test_customer_can_add_and_list_own_favorites(auth_client, customer, other_customer, product, second_product):
    client = auth_client(customer)
    response = client.post("/api/v1/favorites/", {"product_id": product.id}, format="json")
    assert response.status_code == 201

    Favorite.objects.create(user=other_customer, product=second_product)
    list_response = client.get("/api/v1/favorites/")
    product_ids = [item["product"]["id"] for item in list_response.data["results"]]
    assert product_ids == [product.id]


def test_duplicate_favorite_is_rejected(auth_client, customer, product):
    client = auth_client(customer)
    assert client.post("/api/v1/favorites/", {"product_id": product.id}, format="json").status_code == 201
    duplicate = client.post("/api/v1/favorites/", {"product_id": product.id}, format="json")
    assert duplicate.status_code == 400


def test_customer_cannot_delete_other_users_favorite(auth_client, customer, other_customer, product):
    favorite = Favorite.objects.create(user=other_customer, product=product)
    response = auth_client(customer).delete(f"/api/v1/favorites/{favorite.id}/")
    assert response.status_code == 404
    assert Favorite.objects.filter(id=favorite.id).exists()


def test_manager_and_admin_cannot_use_customer_favorites(auth_client, manager, admin_user, product):
    assert auth_client(manager).post("/api/v1/favorites/", {"product_id": product.id}, format="json").status_code == 403
    assert auth_client(admin_user).post("/api/v1/favorites/", {"product_id": product.id}, format="json").status_code == 403
