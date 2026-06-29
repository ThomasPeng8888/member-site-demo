from django.contrib import admin

from .models import (
    MemberTicket,
    PointTransaction,
    StaffPointGrant,
)


@admin.register(MemberTicket)
class MemberTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_no",
        "user",
        "title",
        "ticket_type",
        "status",
        "valid_until",
        "created_at",
    )
    list_filter = ("ticket_type", "status", "valid_until")
    search_fields = ("ticket_no", "title", "user__username", "user__email")


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "transaction_type",
        "points",
        "title",
        "created_at",
    )
    list_filter = ("transaction_type", "created_at")
    search_fields = ("user__username", "user__email", "title", "note")


@admin.register(StaffPointGrant)
class StaffPointGrantAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "staff",
        "purchase_amount",
        "earned_points",
        "created_at",
    )
    list_filter = ("created_at", "staff")
    search_fields = (
        "member__username",
        "member__email",
        "staff__username",
        "staff__email",
        "note",
    )
    readonly_fields = (
        "member",
        "staff",
        "purchase_amount",
        "earned_points",
        "note",
        "created_at",
    )
