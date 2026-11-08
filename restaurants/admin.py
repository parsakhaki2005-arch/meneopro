from django.contrib import admin
from .models import Restaurant, RestaurantMembership, RestaurantSettings


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone", "is_active", "created_at")
    list_filter = ("is_active", "city")
    search_fields = ("name", "slug", "phone", "email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(RestaurantMembership)
class RestaurantMembershipAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("restaurant__name", "user__username", "user__email")


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "currency", "show_prices", "allow_online_orders")
    search_fields = ("restaurant__name",)
