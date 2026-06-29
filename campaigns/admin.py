from django.contrib import admin
from django.utils import timezone

from .models import Campaign, CampaignRegistration, CampaignWinner


class CampaignRegistrationInline(admin.TabularInline):
    model = CampaignRegistration
    extra = 0
    fields = ("user", "status", "register_time")
    readonly_fields = ("register_time",)
    autocomplete_fields = ("user",)


class CampaignWinnerInline(admin.TabularInline):
    model = CampaignWinner
    extra = 0
    fields = (
        "user",
        "winner_type",
        "winner_rank",
        "winner_status",
        "redeem_code",
        "expire_at",
    )
    readonly_fields = ("redeem_code",)
    autocomplete_fields = ("user",)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "campaign_id",
        "campaign_name",
        "status",
        "publish_flag",
        "winner_count",
        "alternate_count",
        "registration_count",
        "primary_winner_count",
        "register_start_at",
        "register_end_at",
        "draw_executed_at",
    )
    list_filter = ("status", "publish_flag", "register_start_at", "register_end_at")
    search_fields = ("campaign_id", "slug", "campaign_name", "prize_name", "campaign_desc")
    prepopulated_fields = {"slug": ("campaign_name",)}
    autocomplete_fields = ("created_by",)
    readonly_fields = (
        "campaign_id",
        "created_at",
        "updated_at",
        "draw_executed_at",
        "registration_count",
        "primary_winner_count",
        "alternate_winner_count",
    )
    fieldsets = (
        ("基本資料", {
            "fields": (
                "campaign_id",
                "campaign_name",
                "slug",
                "campaign_desc",
                "image_emoji",
                "status",
                "publish_flag",
            )
        }),
        ("獎項與名額", {
            "fields": (
                "prize_name",
                "prize_desc",
                "winner_count",
                "alternate_count",
                "redeem_expire_days",
            )
        }),
        ("時間設定", {
            "fields": (
                "register_start_at",
                "register_end_at",
                "draw_at",
                "draw_executed_at",
            )
        }),
        ("規則與內部備註", {
            "fields": ("eligibility_rule", "notes")
        }),
        ("建立資訊", {
            "fields": ("created_by", "created_by_name", "created_at", "updated_at")
        }),
        ("統計", {
            "fields": ("registration_count", "primary_winner_count", "alternate_winner_count")
        }),
    )
    inlines = (CampaignRegistrationInline, CampaignWinnerInline)
    actions = ("publish_campaigns", "close_campaigns", "archive_campaigns")

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        if not obj.created_by_name:
            obj.created_by_name = request.user.get_username()
        super().save_model(request, obj, form, change)

    @admin.action(description="將選取活動設為公開中")
    def publish_campaigns(self, request, queryset):
        updated = queryset.update(status="published", publish_flag=True)
        self.message_user(request, f"已公開 {updated} 個活動抽獎。")

    @admin.action(description="將選取活動設為已截止")
    def close_campaigns(self, request, queryset):
        updated = queryset.update(status="closed")
        self.message_user(request, f"已截止 {updated} 個活動抽獎。")

    @admin.action(description="將選取活動封存並取消公開")
    def archive_campaigns(self, request, queryset):
        updated = queryset.update(status="archived", publish_flag=False)
        self.message_user(request, f"已封存 {updated} 個活動抽獎。")


@admin.register(CampaignRegistration)
class CampaignRegistrationAdmin(admin.ModelAdmin):
    list_display = ("campaign", "user", "status", "register_time")
    list_filter = ("status", "register_time", "campaign")
    search_fields = ("campaign__campaign_name", "campaign__campaign_id", "user__username", "user__email")
    autocomplete_fields = ("campaign", "user")
    readonly_fields = ("register_time", "created_at")


@admin.register(CampaignWinner)
class CampaignWinnerAdmin(admin.ModelAdmin):
    list_display = (
        "winner_id",
        "campaign",
        "user",
        "winner_type",
        "winner_rank",
        "winner_status",
        "redeem_code",
        "expire_at",
        "redeemed_at",
    )
    list_filter = ("winner_type", "winner_status", "draw_time", "expire_at", "campaign")
    search_fields = (
        "winner_id",
        "redeem_code",
        "campaign_name",
        "prize_name",
        "user__username",
        "user__email",
    )
    autocomplete_fields = ("campaign", "user")
    readonly_fields = (
        "winner_id",
        "campaign_name",
        "prize_name",
        "prize_desc",
        "redeem_code",
        "redeem_qr_payload",
        "draw_time",
        "created_at",
    )
    actions = ("mark_redeemed", "mark_void", "mark_expired")

    @admin.action(description="將選取活動兌換券標記為已兌換")
    def mark_redeemed(self, request, queryset):
        updated = queryset.filter(winner_status="unredeemed").update(
            winner_status="redeemed",
            redeemed_at=timezone.now(),
            redeemed_by=str(request.user),
        )
        self.message_user(request, f"已核銷 {updated} 張活動兌換券。")

    @admin.action(description="將選取活動兌換券作廢")
    def mark_void(self, request, queryset):
        updated = queryset.exclude(winner_status="redeemed").update(winner_status="void")
        self.message_user(request, f"已作廢 {updated} 張活動兌換券。")

    @admin.action(description="將選取活動兌換券標記為已過期")
    def mark_expired(self, request, queryset):
        updated = queryset.filter(winner_status="unredeemed").update(winner_status="expired")
        self.message_user(request, f"已標記 {updated} 張活動兌換券為過期。")
