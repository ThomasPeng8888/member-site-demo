from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import line_views, views

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="pages/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register_page, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("member/qr.png", views.member_qr_png, name="member_qr_png"),

    path("line/settings/", line_views.line_settings, name="line_settings"),
    path("line/bind/", line_views.line_bind_start, name="line_bind_start"),
    path("line/callback/", line_views.line_callback, name="line_callback"),
    path("line/unbind/", line_views.line_unbind, name="line_unbind"),
    path("line/toggle-notify/", line_views.line_toggle_notify, name="line_toggle_notify"),
    path("line/webhook/", line_views.line_webhook, name="line_webhook"),
]
