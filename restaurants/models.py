from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


class Restaurant(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)

    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="restaurants/logos/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="restaurants/covers/", blank=True, null=True)

    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_restaurants"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "created_at"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return self.name


class RestaurantMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "مالک"
        ADMIN = "admin", "مدیر"
        EDITOR = "editor", "اپراتور"

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="restaurant_memberships"
    )

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EDITOR)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["restaurant__name", "user__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "user"],
                name="unique_restaurant_user_membership"
            )
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["restaurant", "role"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.restaurant} ({self.role})"


class RestaurantSettings(models.Model):
    class Currency(models.TextChoices):
        TOMAN = "TOMAN", "تومان"
        RIAL = "RIAL", "ریال"
        USD = "USD", "دلار"

    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="settings"
    )

    currency = models.CharField(
        max_length=10,
        choices=Currency.choices,
        default=Currency.TOMAN
    )

    primary_color = models.CharField(
        max_length=7,
        default="#E85D04",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="رنگ باید در قالب HEX باشد مانند #E85D04"
            )
        ]
    )

    show_prices = models.BooleanField(default=True)
    show_unavailable_items = models.BooleanField(default=True)
    allow_online_orders = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings: {self.restaurant.name}"
