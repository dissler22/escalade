from django.urls import path

from . import views_admin


app_name = "accounts_admin"

urlpatterns = [
    path("", views_admin.account_list, name="account-list"),
    path("create/", views_admin.create_account, name="account-create"),
    path("import/", views_admin.import_accounts, name="account-import"),
    path("email-automation/", views_admin.email_automation, name="email-automation"),
    path("<int:user_id>/status/", views_admin.update_account_status, name="account-status"),
    path("<int:user_id>/reset-password/", views_admin.reset_account_password, name="account-reset-password"),
]
