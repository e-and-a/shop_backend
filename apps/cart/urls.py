from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartClearAPIView, CartDetailAPIView, CartItemViewSet


router = DefaultRouter()
router.register("cart/items", CartItemViewSet, basename="cart-item")

urlpatterns = [
    path("cart/", CartDetailAPIView.as_view(), name="cart-detail"),
    path("cart/clear/", CartClearAPIView.as_view(), name="cart-clear"),
    path("", include(router.urls)),
]
