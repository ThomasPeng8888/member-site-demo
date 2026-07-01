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
        "line_status",
        "google_status",
        "line_display_name",
        "line_notify_enabled",
        "created_at",
    )
    search_fields = (
        "member_no",
        "user__username",
        "user__email",
        "phone",
        "line_user_id",
        "line_display_name",
        "google_email",
        "google_sub",
    )
    list_filter = (
        "level",
        "line_notify_enabled",
        "line_bound_at",
        "google_bound_at",
        "created_at",
    )
    readonly_fields = (
        "member_no",
        "line_bound_at",
        "google_bound_at",
        "created_at",
        "updated_at",
    )

    @admin.display(description="LINE 綁定")
    def line_status(self, obj):
        return "已綁定" if obj.line_user_id else "未綁定"

    @admin.display(description="Google 綁定")
    def google_status(self, obj):
        return "已綁定" if obj.google_sub else "未綁定"
