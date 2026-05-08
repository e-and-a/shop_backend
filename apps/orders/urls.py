from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminStatsAPIView, OrderViewSet


router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/stats/", AdminStatsAPIView.as_view(), name="admin-stats"),
]
