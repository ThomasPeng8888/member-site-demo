from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("", include("members.urls")),
    path("", include("aquarium.urls")),
    path("", include("lottery.urls")),
    path("", include("campaigns.urls")),
    path("", include("pages.urls")),
    path("admin/", admin.site.urls),
    # MVP media support for product images uploaded in Django admin.
    # For long-term production media storage, use persistent storage or an object storage service.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
