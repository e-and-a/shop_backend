from decimal import Decimal

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


pytestmark = pytest.mark.django_db


@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    min_price=st.decimals(min_value=0, max_value=3000, places=2),
    max_price=st.decimals(min_value=0, max_value=3000, places=2),
    search=st.text(
        alphabet=st.characters(blacklist_categories=("Cs",), max_codepoint=0xFFFF),
        min_size=0,
        max_size=20,
    ),
)
def test_product_filters_fuzz_do_not_return_server_errors(api_client, product, second_product, min_price, max_price, search):
    response = api_client.get(
        "/api/v1/products/",
        {
            "min_price": str(min_price),
            "max_price": str(max_price),
            "search": search,
            "ordering": "price",
        },
    )

    assert response.status_code < 500
    assert "results" in response.data


@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(quantity=st.integers(min_value=11, max_value=10_000))
def test_cart_quantity_fuzz_rejects_values_above_stock(auth_client, customer, product, quantity):
    product.stock = 10
    product.price = Decimal("100.00")
    product.save(update_fields=("stock", "price", "updated_at"))

    response = auth_client(customer).post(
        "/api/v1/cart/items/",
        {"product_id": product.id, "quantity": quantity},
        format="json",
    )

    assert response.status_code == 400
