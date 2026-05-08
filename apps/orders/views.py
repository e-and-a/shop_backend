from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.common.permissions import IsAdmin, IsAdminOrManager, IsCustomer, IsOwnerOrAdminOrManager

from .models import Order, OrderItem
from .serializers import AdminStatsSerializer, OrderCreateFromCartSerializer, OrderSerializer, OrderStatusUpdateSerializer
from .services import cancel_order, create_order_from_cart


User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=["Orders"]),
    retrieve=extend_schema(tags=["Orders"]),
)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Order.objects.none()
        queryset = Order.objects.select_related("user").prefetch_related("items", "items__product")
        user = self.request.user
        if user.is_superuser or user.role in {"ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(user=user)

    def get_permissions(self):
        if self.action == "create_from_cart":
            return [IsCustomer()]
        if self.action == "set_status":
            return [IsAdminOrManager()]
        if self.action == "cancel":
            return [IsOwnerOrAdminOrManager()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["Orders"],
        request=OrderCreateFromCartSerializer,
        responses={201: OrderSerializer},
    )
    @action(detail=False, methods=["post"], url_path="create-from-cart")
    def create_from_cart(self, request):
        serializer = OrderCreateFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order_from_cart(
            user=request.user,
            delivery_address=serializer.validated_data["delivery_address"],
            phone=serializer.validated_data["phone"],
            comment=serializer.validated_data.get("comment", ""),
        )
        order = self.get_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Orders"],
        request=OrderStatusUpdateSerializer,
        responses={200: OrderSerializer},
    )
    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save(update_fields=("status", "updated_at"))
        return Response(OrderSerializer(order).data)

    @extend_schema(
        tags=["Orders"],
        request=None,
        responses={200: OrderSerializer, 400: OpenApiResponse(description="Order cannot be cancelled.")},
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        self.check_object_permissions(request, order)
        order = cancel_order(order)
        return Response(OrderSerializer(order).data)


class AdminStatsAPIView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(tags=["Admin Stats"], responses={200: AdminStatsSerializer})
    def get(self, request):
        status_counts = {
            row["status"]: row["count"]
            for row in Order.objects.values("status").annotate(count=Count("id")).order_by("status")
        }
        completed_total = (
            Order.objects.filter(status=Order.Status.COMPLETED).aggregate(total=Sum("total_price"))["total"] or 0
        )
        top_products = list(
            OrderItem.objects.filter(order__status=Order.Status.COMPLETED)
            .values("product_id", "product_title_snapshot", "product_sku_snapshot")
            .annotate(quantity_sold=Sum("quantity"), revenue=Sum("subtotal"))
            .order_by("-quantity_sold")[:5]
        )
        low_stock_products = list(
            Product.objects.filter(is_active=True)
            .order_by("stock", "title")
            .values("id", "title", "sku", "stock")[:5]
        )
        data = {
            "users_count": User.objects.count(),
            "customers_count": User.objects.filter(role="CUSTOMER").count(),
            "managers_count": User.objects.filter(role="MANAGER").count(),
            "products_count": Product.objects.count(),
            "active_products_count": Product.objects.filter(is_active=True).count(),
            "orders_count": Order.objects.count(),
            "orders_by_status": status_counts,
            "completed_orders_total": completed_total,
            "top_products": top_products,
            "low_stock_products": low_stock_products,
        }
        return Response(data)
