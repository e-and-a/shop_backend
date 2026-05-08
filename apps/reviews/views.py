from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.catalog.models import Product
from apps.common.permissions import IsCustomer, IsOwnerOrAdminOrManager

from .models import Review
from .serializers import ReviewSerializer


class ProductReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.none()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomer()]
        return [AllowAny()]

    def get_product(self):
        queryset = Product.objects.all()
        user = self.request.user
        if not (user.is_authenticated and (user.is_superuser or user.role in {"ADMIN", "MANAGER"})):
            queryset = queryset.filter(is_active=True)
        return get_object_or_404(queryset, pk=self.kwargs["product_id"])

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Review.objects.none()
        product = self.get_product()
        queryset = Review.objects.filter(product=product).select_related("user", "product")
        user = self.request.user
        if user.is_authenticated and (user.is_superuser or user.role in {"ADMIN", "MANAGER"}):
            return queryset
        return queryset.filter(is_moderated=True)

    @extend_schema(tags=["Reviews"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=["Reviews"], request=ReviewSerializer, responses={201: ReviewSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, product=self.get_product())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == "POST":
            context["product"] = self.get_product()
        return context


@extend_schema_view(
    partial_update=extend_schema(tags=["Reviews"]),
    destroy=extend_schema(tags=["Reviews"]),
)
class ReviewViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.none()
    permission_classes = [IsOwnerOrAdminOrManager]
    http_method_names = ["patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Review.objects.none()
        queryset = Review.objects.select_related("user", "product")
        user = self.request.user
        if user.is_superuser or user.role in {"ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(user=user)
