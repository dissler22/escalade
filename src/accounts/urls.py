from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("password/", views.password_change_view, name="password-change"),
    path("logout/", views.logout_view, name="logout"),
]
