from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, CategoryViewSet, FavoriteViewSet, ProductViewSet


router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("brands", BrandViewSet, basename="brand")
router.register("products", ProductViewSet, basename="product")
router.register("favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("", include(router.urls)),
]
