from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="restaurant_panel/login.html",
            redirect_authenticated_user=True,
            next_page="/panel/"
        ),
        name="login"
    ),
    path("logout/", views.panel_logout, name="logout"),
    path("<slug:slug>/qr/", views.qr_code, name="qr"),
    path("<slug:slug>/settings/", views.restaurant_settings, name="settings"),
    path("", views.index, name="index"),
    path("<slug:slug>/", views.dashboard, name="dashboard"),

    path("<slug:slug>/categories/", views.category_list, name="categories"),
    path("<slug:slug>/categories/add/", views.category_create, name="category_add"),
    path(
        "<slug:slug>/categories/<int:category_id>/edit/",
        views.category_edit,
        name="category_edit"
    ),
    path(
        "<slug:slug>/categories/<int:category_id>/delete/",
        views.category_delete,
        name="category_delete"
    ),

    path("<slug:slug>/items/", views.item_list, name="items"),
    path("<slug:slug>/items/add/", views.item_create, name="item_add"),
    path(
        "<slug:slug>/items/<int:item_id>/edit/",
        views.item_edit,
        name="item_edit"
    ),
    path(
        "<slug:slug>/items/<int:item_id>/delete/",
        views.item_delete,
        name="item_delete"
    ),
]
