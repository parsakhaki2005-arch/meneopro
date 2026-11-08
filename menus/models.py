from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="menus/categories/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "slug"],
                name="unique_category_slug_per_restaurant"
            )
        ]
        indexes = [
            models.Index(fields=["restaurant", "is_active", "sort_order"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.restaurant.name} / {self.name}"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="menu_items"
    )

    category = models.ForeignKey(
        MenuCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items"
    )

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)

    description = models.TextField(blank=True)
    ingredients = models.JSONField(default=list, blank=True)

    price = models.DecimalField(max_digits=14, decimal_places=0)
    discount_price = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to="menus/items/", blank=True, null=True)

    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    preparation_time_minutes = models.PositiveIntegerField(default=0)
    calories = models.PositiveIntegerField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "slug"],
                name="unique_item_slug_per_restaurant"
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="menu_item_price_nonnegative"
            ),
            models.CheckConstraint(
                condition=Q(discount_price__isnull=True) | Q(discount_price__gte=0),
                name="menu_item_discount_nonnegative"
            ),
        ]
        indexes = [
            models.Index(fields=["restaurant", "is_active", "is_available"]),
            models.Index(fields=["restaurant", "category", "sort_order"]),
            models.Index(fields=["restaurant", "is_featured"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        if self.discount_price is not None and self.discount_price < self.price:
            return self.discount_price
        return self.price

    def __str__(self):
        return f"{self.restaurant.name} / {self.name}"
