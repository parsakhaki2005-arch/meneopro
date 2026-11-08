from django.contrib.auth import get_user_model
from django.test import TestCase
from restaurants.models import Restaurant
from .models import MenuCategory, MenuItem


class MenuModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="menu_owner",
            password="test-password-123"
        )
        self.restaurant = Restaurant.objects.create(
            name="رستوران منو",
            slug="menu-restaurant",
            created_by=self.user
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name="غذاهای اصلی",
            slug="main-food"
        )

    def test_category_belongs_to_restaurant(self):
        self.assertEqual(self.category.restaurant, self.restaurant)

    def test_menu_item_creation(self):
        item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="چلوکباب",
            slug="chelo-kebab",
            price=250000,
            ingredients=["برنج", "گوشت"]
        )
        self.assertEqual(item.effective_price, 250000)
        self.assertTrue(item.is_available)

    def test_discount_price(self):
        item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name="غذای تخفیفدار",
            slug="discounted-food",
            price=300000,
            discount_price=250000
        )
        self.assertEqual(item.effective_price, 250000)
