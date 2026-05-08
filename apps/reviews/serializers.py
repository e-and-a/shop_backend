from rest_framework import serializers

from apps.orders.models import Order, OrderItem

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "product",
            "product_title",
            "user",
            "user_email",
            "rating",
            "text",
            "is_moderated",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "product", "product_title", "user", "user_email", "created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or request.user.role not in {"ADMIN", "MANAGER"}:
            self.fields["is_moderated"].read_only = True

    def validate(self, attrs):
        request = self.context.get("request")
        product = self.context.get("product") or (self.instance.product if self.instance else None)
        if not self.instance and Review.objects.filter(product=product, user=request.user).exists():
            raise serializers.ValidationError({"product": "You have already reviewed this product."})
        if not self.instance and not self._user_bought_product(request.user, product):
            raise serializers.ValidationError({"product": "You can review only products from completed orders."})
        return attrs

    def _user_bought_product(self, user, product):
        return OrderItem.objects.filter(
            order__user=user,
            order__status=Order.Status.COMPLETED,
            product=product,
        ).exists()
