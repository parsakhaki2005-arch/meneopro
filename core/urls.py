from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("m/<slug:slug>/", views.public_menu, name="public_menu"),
]
