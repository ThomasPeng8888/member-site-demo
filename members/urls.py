from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import line_views, social_views, views

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

    path("auth/google/start/", social_views.social_google_start, name="social_google_start"),
    path("auth/google/callback/", social_views.social_google_callback, name="social_google_callback"),
    path("auth/line/start/", social_views.social_line_start, name="social_line_start"),
    path("auth/line/callback/", social_views.social_line_callback, name="social_line_callback"),
    path("auth/line/complete-email/", social_views.social_line_complete_email, name="social_line_complete_email"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("member/qr.png", views.member_qr_png, name="member_qr_png"),

    path("line/settings/", line_views.line_settings, name="line_settings"),
    path("line/bind/", line_views.line_bind_start, name="line_bind_start"),
    path("line/callback/", line_views.line_callback, name="line_callback"),
    path("line/unbind/", line_views.line_unbind, name="line_unbind"),
    path("line/toggle-notify/", line_views.line_toggle_notify, name="line_toggle_notify"),
    path("line/webhook/", line_views.line_webhook, name="line_webhook"),
]
