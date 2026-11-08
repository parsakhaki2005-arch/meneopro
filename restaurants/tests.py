from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Restaurant, RestaurantMembership, RestaurantSettings


class RestaurantModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="restaurant_owner",
            password="test-password-123"
        )
        self.restaurant = Restaurant.objects.create(
            name="رستوران آزمایشی",
            slug="test-restaurant",
            created_by=self.user
        )

    def test_restaurant_creation(self):
        self.assertEqual(self.restaurant.name, "رستوران آزمایشی")
        self.assertTrue(self.restaurant.is_active)

    def test_membership_is_unique(self):
        RestaurantMembership.objects.create(
            restaurant=self.restaurant,
            user=self.user,
            role=RestaurantMembership.Role.OWNER
        )
        self.assertEqual(
            RestaurantMembership.objects.filter(
                restaurant=self.restaurant,
                user=self.user
            ).count(),
            1
        )

    def test_restaurant_settings(self):
        settings = RestaurantSettings.objects.create(
            restaurant=self.restaurant
        )
        self.assertEqual(settings.currency, "TOMAN")
        self.assertTrue(settings.show_prices)
