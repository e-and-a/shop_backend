from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_title_snapshot",
        "product_sku_snapshot",
        "price_snapshot",
        "quantity",
        "subtotal",
    )
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "phone", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("id", "user__email", "phone", "delivery_address", "items__product_sku_snapshot")
    readonly_fields = ("total_price", "created_at", "updated_at")
    autocomplete_fields = ("user",)
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_title_snapshot", "product_sku_snapshot", "price_snapshot", "quantity", "subtotal")
    list_filter = ("order__status",)
    search_fields = ("order__id", "product_title_snapshot", "product_sku_snapshot")
    readonly_fields = ("product_title_snapshot", "product_sku_snapshot", "price_snapshot", "subtotal")
    autocomplete_fields = ("order", "product")
