from django.contrib import admin
from django.utils import timezone

from .models import LotteryPrize, LotterySpin


@admin.register(LotteryPrize)
class LotteryPrizeAdmin(admin.ModelAdmin):
    list_display = (
        "prize_code",
        "prize_name",
        "weight",
        "stock",
        "points_cost",
        "enabled",
        "sort_order",
        "updated_at",
    )
    list_filter = ("enabled", "created_at")
    search_fields = ("prize_code", "prize_name", "prize_desc")
    ordering = ("sort_order", "id")


@admin.register(LotterySpin)
class LotterySpinAdmin(admin.ModelAdmin):
    list_display = (
        "spin_code",
        "user",
        "prize_name",
        "cost_points",
        "balance_after",
        "coupon_status",
        "redeem_code",
        "expire_at",
        "spin_time",
    )
    list_filter = ("coupon_status", "result_status", "spin_time", "expire_at")
    search_fields = (
        "spin_code",
        "redeem_code",
        "user__username",
        "user__email",
        "prize_name",
    )
    readonly_fields = (
        "spin_code",
        "spin_time",
        "user",
        "cost_points",
        "prize",
        "prize_name",
        "stock_before",
        "stock_after",
        "balance_after",
        "redeem_code",
        "redeem_qr_payload",
        "created_at",
    )
    actions = ("mark_redeemed", "mark_void")

    @admin.action(description="將選取兌換券標記為已兌換")
    def mark_redeemed(self, request, queryset):
        updated = queryset.filter(coupon_status="unredeemed").update(
            coupon_status="redeemed",
            redeemed_at=timezone.now(),
            redeemed_by=str(request.user),
        )
        self.message_user(request, f"已核銷 {updated} 張兌換券。")

    @admin.action(description="將選取兌換券作廢")
    def mark_void(self, request, queryset):
        updated = queryset.exclude(coupon_status="redeemed").update(
            coupon_status="void",
        )
        self.message_user(request, f"已作廢 {updated} 張兌換券。")