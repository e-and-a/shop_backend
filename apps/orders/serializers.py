from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_title_snapshot",
            "product_sku_snapshot",
            "price_snapshot",
            "quantity",
            "subtotal",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "user_email",
            "status",
            "total_price",
            "delivery_address",
            "phone",
            "comment",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "user_email",
            "status",
            "total_price",
            "items",
            "created_at",
            "updated_at",
        )


class OrderCreateFromCartSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    phone = serializers.CharField(max_length=30)
    comment = serializers.CharField(required=False, allow_blank=True)


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)


class AdminStatsSerializer(serializers.Serializer):
    users_count = serializers.IntegerField()
    customers_count = serializers.IntegerField()
    managers_count = serializers.IntegerField()
    products_count = serializers.IntegerField()
    active_products_count = serializers.IntegerField()
    orders_count = serializers.IntegerField()
    orders_by_status = serializers.DictField(child=serializers.IntegerField())
    completed_orders_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    top_products = serializers.ListField(child=serializers.DictField())
    low_stock_products = serializers.ListField(child=serializers.DictField())
