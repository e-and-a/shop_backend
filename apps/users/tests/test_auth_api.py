import pytest
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


pytestmark = pytest.mark.django_db


def test_register_creates_customer_and_does_not_return_password(api_client, django_user_model):
    response = api_client.post(
        "/api/v1/auth/register/",
        {
            "email": "new@example.com",
            "username": "",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "first_name": "New",
            "last_name": "Customer",
            "phone": "+79991112233",
            "role": "ADMIN",
            "is_staff": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["role"] == "CUSTOMER"
    assert "password" not in response.data

    user = django_user_model.objects.get(email="new@example.com")
    assert user.role == "CUSTOMER"
    assert user.username is None
    assert not user.is_staff
    assert not user.is_superuser


def test_login_refresh_logout_and_me_flow(api_client, customer):
    login = api_client.post(
        "/api/v1/auth/login/",
        {"email": customer.email, "password": "password12345"},
        format="json",
    )
    assert login.status_code == 200
    assert "access" in login.data
    assert "refresh" in login.data
    assert login.data["user"]["email"] == customer.email
    assert "password" not in login.data["user"]

    refresh = api_client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": login.data["refresh"]},
        format="json",
    )
    assert refresh.status_code == 200
    assert "access" in refresh.data

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    me = api_client.get("/api/v1/auth/me/")
    assert me.status_code == 200
    assert me.data["email"] == customer.email
    assert "password" not in me.data

    patch = api_client.patch("/api/v1/auth/me/", {"first_name": "Updated"}, format="json")
    assert patch.status_code == 200
    assert patch.data["first_name"] == "Updated"

    current_refresh = refresh.data.get("refresh", login.data["refresh"])
    blacklisted_before_logout = BlacklistedToken.objects.count()
    logout = api_client.post("/api/v1/auth/logout/", {"refresh": current_refresh}, format="json")
    assert logout.status_code == 205
    assert BlacklistedToken.objects.count() == blacklisted_before_logout + 1


def test_public_registration_cannot_create_manager_or_admin(api_client, django_user_model):
    response = api_client.post(
        "/api/v1/auth/register/",
        {
            "email": "role-attempt@example.com",
            "password": "strongpass123",
            "password_confirm": "strongpass123",
            "role": "MANAGER",
        },
        format="json",
    )

    assert response.status_code == 201
    user = django_user_model.objects.get(email="role-attempt@example.com")
    assert user.role == "CUSTOMER"
    assert not user.is_staff
