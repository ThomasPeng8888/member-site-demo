from django.contrib import admin
from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "member_no",
        "user",
        "phone",
        "points",
        "level",
        "line_user_id",
        "created_at",
    )
    search_fields = (
        "member_no",
        "user__username",
        "user__email",
        "phone",
        "line_user_id",
    )
    list_filter = (
        "level",
        "created_at",
    )