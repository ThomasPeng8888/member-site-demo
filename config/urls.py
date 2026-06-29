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
]

# Local media support for development. When Cloudflare R2 is enabled, uploaded
# images are served by the public R2 URL instead of this Django media route.
if not getattr(settings, "USE_R2_MEDIA", False):
    urlpatterns.append(
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})
    )
