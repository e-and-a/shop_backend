from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.cart.models import Cart
from apps.catalog.models import Product

from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(user, delivery_address, phone, comment=""):
    try:
        cart = Cart.objects.select_for_update().get(user=user)
    except Cart.DoesNotExist as exc:
        raise ValidationError({"cart": "Cart is empty."}) from exc

    cart_items = list(cart.items.select_related("product"))
    if not cart_items:
        raise ValidationError({"cart": "Cart is empty."})

    product_ids = [item.product_id for item in cart_items]
    products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    quantities = defaultdict(int)
    total_price = Decimal("0.00")
    order_items = []

    for cart_item in cart_items:
        product = products[cart_item.product_id]
        if not product.is_active:
            raise ValidationError({"cart": f"Product '{product.title}' is inactive."})
        if product.stock < cart_item.quantity:
            raise ValidationError({"cart": f"Not enough stock for '{product.title}'."})

        subtotal = product.price * cart_item.quantity
        total_price += subtotal
        quantities[product.id] += cart_item.quantity
        order_items.append(
            OrderItem(
                product=product,
                product_title_snapshot=product.title,
                product_sku_snapshot=product.sku,
                price_snapshot=product.price,
                quantity=cart_item.quantity,
                subtotal=subtotal,
            )
        )

    order = Order.objects.create(
        user=user,
        total_price=total_price,
        delivery_address=delivery_address,
        phone=phone,
        comment=comment,
    )

    for item in order_items:
        item.order = order
    OrderItem.objects.bulk_create(order_items)

    for product_id, quantity in quantities.items():
        product = products[product_id]
        product.stock -= quantity
        product.save(update_fields=("stock", "updated_at"))

    cart.items.all().delete()
    cart.save(update_fields=("updated_at",))
    return order


@transaction.atomic
def cancel_order(order):
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.status not in {Order.Status.CREATED, Order.Status.PROCESSING}:
        raise ValidationError({"status": "Only CREATED and PROCESSING orders can be cancelled."})

    product_ids = list(order.items.values_list("product_id", flat=True))
    products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    for item in order.items.all():
        product = products[item.product_id]
        product.stock += item.quantity
        product.save(update_fields=("stock", "updated_at"))

    order.status = Order.Status.CANCELLED
    order.save(update_fields=("status", "updated_at"))
    return order
