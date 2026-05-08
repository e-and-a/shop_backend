import pytest

from apps.reviews.models import Review


pytestmark = pytest.mark.django_db


def test_customer_can_create_review_for_completed_purchase(auth_client, customer, product, completed_order):
    response = auth_client(customer).post(
        f"/api/v1/products/{product.id}/reviews/",
        {"rating": 5, "text": "Excellent"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["rating"] == 5
    assert response.data["is_moderated"] is False


def test_customer_cannot_review_without_completed_purchase(auth_client, customer, product):
    response = auth_client(customer).post(
        f"/api/v1/products/{product.id}/reviews/",
        {"rating": 4, "text": "No purchase"},
        format="json",
    )

    assert response.status_code == 400


def test_customer_cannot_review_same_product_twice(auth_client, customer, product, completed_order):
    client = auth_client(customer)
    assert client.post(
        f"/api/v1/products/{product.id}/reviews/",
        {"rating": 5, "text": "First"},
        format="json",
    ).status_code == 201

    duplicate = client.post(
        f"/api/v1/products/{product.id}/reviews/",
        {"rating": 4, "text": "Second"},
        format="json",
    )
    assert duplicate.status_code == 400


def test_public_reviews_show_only_moderated(api_client, product, customer, other_customer):
    moderated = Review.objects.create(product=product, user=customer, rating=5, text="Visible", is_moderated=True)
    Review.objects.create(product=product, user=other_customer, rating=1, text="Hidden", is_moderated=False)

    response = api_client.get(f"/api/v1/products/{product.id}/reviews/")
    ids = [item["id"] for item in response.data["results"]]

    assert ids == [moderated.id]


def test_manager_can_moderate_review(auth_client, manager, product, customer):
    review = Review.objects.create(product=product, user=customer, rating=4, text="Pending", is_moderated=False)

    response = auth_client(manager).patch(f"/api/v1/reviews/{review.id}/", {"is_moderated": True}, format="json")

    assert response.status_code == 200
    review.refresh_from_db()
    assert review.is_moderated is True


def test_customer_cannot_moderate_review(auth_client, customer, product, completed_order):
    review = Review.objects.create(product=product, user=customer, rating=4, text="Own", is_moderated=False)

    response = auth_client(customer).patch(f"/api/v1/reviews/{review.id}/", {"is_moderated": True}, format="json")

    assert response.status_code == 200
    review.refresh_from_db()
    assert review.is_moderated is False


def test_product_rating_recalculates_from_moderated_reviews(api_client, product, customer, other_customer):
    Review.objects.create(product=product, user=customer, rating=4, text="Good", is_moderated=True)
    Review.objects.create(product=product, user=other_customer, rating=2, text="Ok", is_moderated=True)

    response = api_client.get(f"/api/v1/products/{product.id}/")

    assert response.status_code == 200
    assert response.data["average_rating"] == 3.0
    assert response.data["reviews_count"] == 2
