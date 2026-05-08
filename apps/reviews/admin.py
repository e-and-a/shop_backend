from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "is_moderated", "created_at", "updated_at")
    list_filter = ("rating", "is_moderated", "created_at", "updated_at")
    search_fields = ("product__title", "product__sku", "user__email", "text")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("product", "user")
