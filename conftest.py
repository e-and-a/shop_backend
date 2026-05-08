from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cart.models import Cart, CartItem
from apps.catalog.models import Brand, Category, Product
from apps.orders.models import Order, OrderItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    def _auth_client(user):
        api_client = APIClient()
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return api_client

    return _auth_client


@pytest.fixture
def create_user(django_user_model):
    counter = {"value": 0}

    def _create_user(role="CUSTOMER", password="password12345", **kwargs):
        counter["value"] += 1
        email = kwargs.pop("email", f"user{counter['value']}@example.com")
        defaults = {
            "role": role,
            "first_name": "Test",
            "last_name": "User",
            "phone": "+79990000000",
            "is_staff": role in {"ADMIN", "MANAGER"},
            "is_superuser": role == "ADMIN",
        }
        defaults.update(kwargs)
        return django_user_model.objects.create_user(email=email, password=password, **defaults)

    return _create_user


@pytest.fixture
def customer(create_user):
    return create_user(email="customer@test.local", role="CUSTOMER")


@pytest.fixture
def other_customer(create_user):
    return create_user(email="other@test.local", role="CUSTOMER")


@pytest.fixture
def manager(create_user):
    return create_user(email="manager@test.local", role="MANAGER")


@pytest.fixture
def admin_user(create_user):
    return create_user(email="admin@test.local", role="ADMIN")


@pytest.fixture
def category():
    return Category.objects.create(name="Smartphones", slug="smartphones", is_active=True)


@pytest.fixture
def brand():
    return Brand.objects.create(name="Apple", slug="apple", country="USA", is_active=True)


@pytest.fixture
def product(category, brand, manager):
    return Product.objects.create(
        category=category,
        brand=brand,
        title="iPhone Test",
        slug="iphone-test",
        description="Test smartphone",
        price=Decimal("1000.00"),
        old_price=Decimal("1100.00"),
        stock=10,
        sku="PHONE-TEST-1",
        characteristics={"screen_size": "6.1", "memory": "128GB"},
        warranty_months=12,
        is_active=True,
        created_by=manager,
    )


@pytest.fixture
def second_product(category, brand, manager):
    return Product.objects.create(
        category=category,
        brand=brand,
        title="Laptop Test",
        slug="laptop-test",
        description="Test laptop with fast SSD",
        price=Decimal("2000.00"),
        stock=3,
        sku="LAP-TEST-1",
        characteristics={"processor": "Ryzen", "ram": "16GB"},
        warranty_months=24,
        is_active=True,
        created_by=manager,
    )


@pytest.fixture
def cart_with_item(customer, product):
    cart, _ = Cart.objects.get_or_create(user=customer)
    item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart, item


@pytest.fixture
def completed_order(customer, product):
    order = Order.objects.create(
        user=customer,
        status=Order.Status.COMPLETED,
        total_price=product.price,
        delivery_address="Test address",
        phone="+79990000000",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_title_snapshot=product.title,
        product_sku_snapshot=product.sku,
        price_snapshot=product.price,
        quantity=1,
        subtotal=product.price,
    )
    return order
