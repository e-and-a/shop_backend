from rest_framework import serializers

from apps.catalog.models import Product
from apps.catalog.serializers import ProductShortSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity", "subtotal", "created_at", "updated_at")
        read_only_fields = ("id", "product", "subtotal", "created_at", "updated_at")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "items_count", "total_price", "created_at", "updated_at")
        read_only_fields = ("id", "items", "items_count", "total_price", "created_at", "updated_at")


class CartItemWriteSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.filter(is_active=True),
        write_only=True,
        required=True,
    )
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ("id", "product_id", "quantity")
        read_only_fields = ("id",)

    def validate(self, attrs):
        if self.instance and "product" in attrs:
            raise serializers.ValidationError({"product_id": "Product cannot be changed for an existing cart item."})
        product = attrs.get("product") or self.instance.product
        quantity = attrs.get("quantity", self.instance.quantity if self.instance else 1)
        if not product.is_active:
            raise serializers.ValidationError({"product_id": "Inactive product cannot be added to cart."})
        if product.stock <= 0:
            raise serializers.ValidationError({"product_id": "Product is out of stock."})
        if quantity > product.stock:
            raise serializers.ValidationError({"quantity": "Requested quantity exceeds product stock."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        cart, _ = Cart.objects.get_or_create(user=user)
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            new_quantity = item.quantity + quantity
            if new_quantity > product.stock:
                raise serializers.ValidationError({"quantity": "Requested quantity exceeds product stock."})
            item.quantity = new_quantity
            item.save(update_fields=("quantity", "updated_at"))
        cart.save(update_fields=("updated_at",))
        return item

    def update(self, instance, validated_data):
        quantity = validated_data.get("quantity", instance.quantity)
        if quantity > instance.product.stock:
            raise serializers.ValidationError({"quantity": "Requested quantity exceeds product stock."})
        instance.quantity = quantity
        instance.save(update_fields=("quantity", "updated_at"))
        instance.cart.save(update_fields=("updated_at",))
        return instance
