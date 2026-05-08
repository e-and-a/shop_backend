from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.permissions import IsAdmin, IsAdminOrManager, IsAuthenticatedOrReadOnlyForCatalog, IsCustomer

from .filters import ProductFilter
from .models import Brand, Category, Favorite, Product
from .serializers import BrandSerializer, CategorySerializer, FavoriteSerializer, ProductSerializer


class PublicCatalogQuerysetMixin:
    def filter_public_queryset(self, queryset):
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or user.role in {"ADMIN", "MANAGER"}):
            return queryset
        return queryset.filter(is_active=True)


@extend_schema_view(
    list=extend_schema(tags=["Catalog"]),
    retrieve=extend_schema(tags=["Catalog"]),
    create=extend_schema(tags=["Catalog"]),
    partial_update=extend_schema(tags=["Catalog"]),
    destroy=extend_schema(tags=["Catalog"]),
)
class CategoryViewSet(PublicCatalogQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ("is_active",)
    search_fields = ("name", "description", "slug")
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        return self.filter_public_queryset(super().get_queryset())

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdmin()]
        if self.action in {"create", "update", "partial_update"}:
            return [IsAdminOrManager()]
        return [AllowAny()]


@extend_schema_view(
    list=extend_schema(tags=["Brands"]),
    retrieve=extend_schema(tags=["Brands"]),
    create=extend_schema(tags=["Brands"]),
    partial_update=extend_schema(tags=["Brands"]),
    destroy=extend_schema(tags=["Brands"]),
)
class BrandViewSet(PublicCatalogQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ("is_active", "country")
    search_fields = ("name", "description", "slug", "country")
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_queryset(self):
        return self.filter_public_queryset(super().get_queryset())

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdmin()]
        if self.action in {"create", "update", "partial_update"}:
            return [IsAdminOrManager()]
        return [AllowAny()]


@extend_schema_view(
    list=extend_schema(tags=["Catalog"]),
    retrieve=extend_schema(tags=["Catalog"]),
    create=extend_schema(tags=["Catalog"]),
    partial_update=extend_schema(tags=["Catalog"]),
    destroy=extend_schema(tags=["Catalog"]),
)
class ProductViewSet(PublicCatalogQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("category", "brand", "created_by")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticatedOrReadOnlyForCatalog]
    filterset_class = ProductFilter
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ("title", "description", "sku")
    ordering_fields = ("price", "created_at", "rating", "stock")
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            rating=Avg("reviews__rating", filter=Q(reviews__is_moderated=True)),
            reviews_count=Count("reviews", filter=Q(reviews__is_moderated=True), distinct=True),
        )
        queryset = self.filter_public_queryset(queryset)
        user = self.request.user
        if not (user.is_authenticated and (user.is_superuser or user.role in {"ADMIN", "MANAGER"})):
            queryset = queryset.filter(category__is_active=True, brand__is_active=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = False
        product.save(update_fields=("is_active", "updated_at"))
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Favorites"]),
    create=extend_schema(tags=["Favorites"]),
    destroy=extend_schema(tags=["Favorites"]),
)
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.none()
    permission_classes = [IsCustomer]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user).select_related(
            "product", "product__category", "product__brand"
        )
