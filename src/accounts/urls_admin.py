from django.urls import path

from . import views_admin


app_name = "accounts_admin"

urlpatterns = [
    path("", views_admin.account_list, name="account-list"),
    path("<int:user_id>/status/", views_admin.update_account_status, name="account-status"),
]
