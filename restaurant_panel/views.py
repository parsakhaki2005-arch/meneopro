from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from restaurants.models import Restaurant, RestaurantMembership, RestaurantSettings
from menus.models import MenuCategory, MenuItem
from .forms import CategoryForm, ItemForm

LOGIN_URL = "/panel/login/"

def accessible_restaurants(user):
    if user.is_superuser:
        return Restaurant.objects.all().order_by("name")

    membership_ids = RestaurantMembership.objects.filter(
        user=user, is_active=True
    ).values_list("restaurant_id", flat=True)

    return Restaurant.objects.filter(
        Q(created_by=user) | Q(pk__in=membership_ids)
    ).distinct().order_by("name")

def get_managed_restaurant(user, slug):
    restaurant = get_object_or_404(
        Restaurant, slug=slug, is_active=True
    )
    if not accessible_restaurants(user).filter(pk=restaurant.pk).exists():
        raise PermissionDenied("شما اجازه مدیریت این رستوران را ندارید.")
    return restaurant

@login_required(login_url=LOGIN_URL)
def index(request):
    restaurants = accessible_restaurants(request.user)
    if restaurants.count() == 1:
        return redirect("panel:dashboard", slug=restaurants.first().slug)
    return render(request, "restaurant_panel/index.html", {
        "restaurants": restaurants
    })

@login_required(login_url=LOGIN_URL)
def dashboard(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    items = MenuItem.objects.filter(restaurant=restaurant)

    recent_items = (
        items.order_by("-created_at")[:6]
        if any(f.name == "created_at" for f in MenuItem._meta.fields)
        else items.order_by("-id")[:6]
    )

    return render(request, "restaurant_panel/dashboard.html", {
        "restaurant": restaurant,
        "category_count": categories.count(),
        "item_count": items.count(),
        "available_count": items.filter(is_active=True, is_available=True).count(),
        "unavailable_count": items.filter(is_available=False).count(),
        "recent_items": recent_items,
    })

@login_required(login_url=LOGIN_URL)
def category_list(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    categories = MenuCategory.objects.filter(
        restaurant=restaurant
    ).order_by("sort_order", "name")
    return render(request, "restaurant_panel/categories.html", {
        "restaurant": restaurant, "categories": categories
    })

@login_required(login_url=LOGIN_URL)
def category_create(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    form = CategoryForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        category.restaurant = restaurant
        category.save()
        messages.success(request, "دستهبندی با موفقیت ایجاد شد.")
        return redirect("panel:categories", slug=slug)

    return render(request, "restaurant_panel/form.html", {
        "restaurant": restaurant,
        "form": form,
        "page_title": "افزودن دستهبندی",
        "cancel_url": "panel:categories",
    })

@login_required(login_url=LOGIN_URL)
def category_edit(request, slug, category_id):
    restaurant = get_managed_restaurant(request.user, slug)
    category = get_object_or_404(
        MenuCategory, pk=category_id, restaurant=restaurant
    )
    form = CategoryForm(
        request.POST or None, request.FILES or None, instance=category
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "دستهبندی با موفقیت ویرایش شد.")
        return redirect("panel:categories", slug=slug)

    return render(request, "restaurant_panel/form.html", {
        "restaurant": restaurant,
        "form": form,
        "page_title": "ویرایش دستهبندی",
        "cancel_url": "panel:categories",
    })

@login_required(login_url=LOGIN_URL)
@require_POST
def category_delete(request, slug, category_id):
    restaurant = get_managed_restaurant(request.user, slug)
    category = get_object_or_404(
        MenuCategory, pk=category_id, restaurant=restaurant
    )
    category.delete()
    messages.success(request, "دستهبندی حذف شد.")
    return redirect("panel:categories", slug=slug)

@login_required(login_url=LOGIN_URL)
def item_list(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    items = MenuItem.objects.filter(
        restaurant=restaurant
    ).select_related("category").order_by("sort_order", "name")
    return render(request, "restaurant_panel/items.html", {
        "restaurant": restaurant, "items": items
    })

@login_required(login_url=LOGIN_URL)
def item_create(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    form = ItemForm(
        request.POST or None, request.FILES or None, restaurant=restaurant
    )

    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.restaurant = restaurant

        if item.category and item.category.restaurant_id != restaurant.id:
            raise PermissionDenied("دستهبندی انتخابشده متعلق به این رستوران نیست.")

        item.save()
        messages.success(request, "غذای جدید با موفقیت ثبت شد.")
        return redirect("panel:items", slug=slug)

    return render(request, "restaurant_panel/form.html", {
        "restaurant": restaurant,
        "form": form,
        "page_title": "افزودن غذای جدید",
        "cancel_url": "panel:items",
    })

@login_required(login_url=LOGIN_URL)
def item_edit(request, slug, item_id):
    restaurant = get_managed_restaurant(request.user, slug)
    item = get_object_or_404(
        MenuItem, pk=item_id, restaurant=restaurant
    )
    form = ItemForm(
        request.POST or None, request.FILES or None,
        instance=item, restaurant=restaurant
    )

    if request.method == "POST" and form.is_valid():
        saved_item = form.save(commit=False)
        saved_item.restaurant = restaurant

        if saved_item.category and saved_item.category.restaurant_id != restaurant.id:
            raise PermissionDenied("دستهبندی انتخابشده متعلق به این رستوران نیست.")

        saved_item.save()
        messages.success(request, "اطلاعات غذا با موفقیت ویرایش شد.")
        return redirect("panel:items", slug=slug)

    return render(request, "restaurant_panel/form.html", {
        "restaurant": restaurant,
        "form": form,
        "page_title": "ویرایش غذا",
        "cancel_url": "panel:items",
    })

@login_required(login_url=LOGIN_URL)
@require_POST
def item_delete(request, slug, item_id):
    restaurant = get_managed_restaurant(request.user, slug)
    item = get_object_or_404(
        MenuItem, pk=item_id, restaurant=restaurant
    )
    item.delete()
    messages.success(request, "غذا حذف شد.")
    return redirect("panel:items", slug=slug)

@login_required(login_url=LOGIN_URL)
@require_POST
def panel_logout(request):
    logout(request)
    return redirect("panel:login")

@login_required(login_url=LOGIN_URL)
def restaurant_settings(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    settings_obj, created = RestaurantSettings.objects.get_or_create(
        restaurant=restaurant
    )

    editable_names = [
        "currency", "primary_color", "show_prices",
        "show_unavailable_items", "allow_online_orders",
    ]
    available_names = {
        field.name for field in RestaurantSettings._meta.fields
    }
    editable_fields = [
        name for name in editable_names if name in available_names
    ]

    SettingsForm = modelform_factory(
        RestaurantSettings, fields=editable_fields
    )
    form = SettingsForm(request.POST or None, instance=settings_obj)

    labels = {
        "currency": "واحد پول",
        "primary_color": "رنگ اصلی منو",
        "show_prices": "نمایش قیمتها",
        "show_unavailable_items": "نمایش محصولات ناموجود",
        "allow_online_orders": "فعال بودن سفارش آنلاین",
    }
    for name, label in labels.items():
        if name in form.fields:
            form.fields[name].label = label
            form.fields[name].widget.attrs["class"] = (
                "form-check-input" if form.fields[name].widget.__class__.__name__ == "CheckboxInput"
                else "form-control"
            )
            form.fields[name].widget.attrs["dir"] = "rtl"

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تنظیمات منو با موفقیت ذخیره شد.")
        return redirect("panel:settings", slug=slug)

    return render(request, "restaurant_panel/settings.html", {
        "restaurant": restaurant, "form": form
    })

@login_required(login_url=LOGIN_URL)
def qr_code(request, slug):
    restaurant = get_managed_restaurant(request.user, slug)
    menu_url = request.build_absolute_uri(f"/m/{restaurant.slug}/")
    return render(request, "restaurant_panel/qr_code.html", {
        "restaurant": restaurant, "menu_url": menu_url
    })
