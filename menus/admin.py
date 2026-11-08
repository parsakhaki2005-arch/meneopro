from django.contrib import admin
from .models import MenuCategory, MenuItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "is_active", "sort_order")
    list_filter = ("restaurant", "is_active")
    search_fields = ("name", "restaurant__name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name", "restaurant", "category", "price",
        "discount_price", "is_available", "is_featured", "is_active"
    )
    list_filter = (
        "restaurant", "category", "is_available", "is_featured", "is_active"
    )
    search_fields = ("name", "slug", "description", "restaurant__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
