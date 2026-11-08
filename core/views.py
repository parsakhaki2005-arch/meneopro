from django.shortcuts import get_object_or_404, render
from django.db.models import Prefetch

from restaurants.models import Restaurant, RestaurantSettings
from menus.models import MenuCategory, MenuItem


def public_menu(request, slug):
    restaurant = get_object_or_404(
        Restaurant,
        slug=slug,
        is_active=True
    )

    try:
        menu_settings = restaurant.settings
    except RestaurantSettings.DoesNotExist:
        menu_settings = None

    categories = MenuCategory.objects.filter(
        restaurant=restaurant,
        is_active=True
    ).order_by("sort_order", "name").prefetch_related(
        Prefetch(
            "items",
            queryset=MenuItem.objects.filter(
                restaurant=restaurant,
                is_active=True
            ).order_by("sort_order", "name"),
            to_attr="visible_items"
        )
    )

    return render(
        request,
        "menu/public_menu.html",
        {
            "restaurant": restaurant,
            "categories": categories,
            "menu_settings": menu_settings,
        }
    )
