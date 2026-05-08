from django.contrib import admin

from .models import Brand, Category, Favorite, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "country", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "country", "created_at")
    search_fields = ("name", "slug", "country", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "sku", "category", "brand", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category", "brand", "created_at", "warranty_months")
    search_fields = ("title", "slug", "sku", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("category", "brand", "created_by")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "product__title", "product__sku")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "product")
