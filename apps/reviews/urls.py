from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProductReviewListCreateAPIView, ReviewViewSet


router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("products/<int:product_id>/reviews/", ProductReviewListCreateAPIView.as_view(), name="product-reviews"),
    path("", include(router.urls)),
]
