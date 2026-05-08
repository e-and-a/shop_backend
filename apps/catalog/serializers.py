from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Brand, Category, Favorite, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "country", "description", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "category_name",
            "brand",
            "brand_name",
            "title",
            "slug",
            "description",
            "price",
            "old_price",
            "stock",
            "sku",
            "image",
            "characteristics",
            "warranty_months",
            "is_active",
            "created_by",
            "average_rating",
            "reviews_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "average_rating", "reviews_count", "created_at", "updated_at")

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_average_rating(self, obj):
        rating = getattr(obj, "rating", None)
        if rating is None:
            return None
        return round(float(rating), 2)

    @extend_schema_field(OpenApiTypes.INT)
    def get_reviews_count(self, obj):
        return getattr(obj, "reviews_count", 0)


class ProductShortSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "title", "slug", "sku", "price", "stock", "image", "category_name", "brand_name")


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.filter(is_active=True, stock__gt=0),
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ("id", "product", "product_id", "created_at")
        read_only_fields = ("id", "product", "created_at")

    def validate(self, attrs):
        request = self.context["request"]
        product = attrs["product"]
        if Favorite.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError({"product_id": "Product is already in favorites."})
        return attrs

    def create(self, validated_data):
        return Favorite.objects.create(user=self.context["request"].user, **validated_data)
