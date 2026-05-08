from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsCustomer

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartItemWriteSerializer, CartSerializer


def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartDetailAPIView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Cart"], responses={200: CartSerializer})
    def get(self, request):
        cart = get_user_cart(request.user)
        queryset = Cart.objects.prefetch_related("items__product", "items__product__category", "items__product__brand")
        cart = queryset.get(pk=cart.pk)
        return Response(CartSerializer(cart).data)


class CartClearAPIView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Cart"], responses={204: None})
    def delete(self, request):
        cart = get_user_cart(request.user)
        cart.items.all().delete()
        cart.save(update_fields=("updated_at",))
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    create=extend_schema(tags=["Cart"]),
    partial_update=extend_schema(tags=["Cart"]),
    destroy=extend_schema(tags=["Cart"]),
)
class CartItemViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsCustomer]
    queryset = CartItem.objects.none()
    http_method_names = ["post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return CartItem.objects.none()
        cart = get_user_cart(self.request.user)
        return CartItem.objects.filter(cart=cart).select_related("product", "product__category", "product__brand")

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return CartItemWriteSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(CartItemSerializer(item).data)
