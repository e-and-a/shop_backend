from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "items_count", "total_price", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at", "total_price", "items_count")
    autocomplete_fields = ("user",)
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("cart__user__email", "product__title", "product__sku")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("cart", "product")
