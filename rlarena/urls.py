from django.contrib import admin
from django.urls import path, include
from core import views, admin_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("language/<str:code>/", views.set_language, name="set_language"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("admin-panel/", admin_views.admin_panel, name="admin_panel"),
    path("admin-panel/user/<int:user_id>/", admin_views.admin_user_detail, name="admin_user"),
    path("admin-panel/user/<int:user_id>/toggle/", admin_views.toggle_user, name="admin_toggle"),
    path("admin-panel/export.csv", admin_views.export_csv, name="admin_export"),
    path("api/", include("core.api_urls")),
]
