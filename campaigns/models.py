from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string


DEFAULT_CAMPAIGN_REDEEM_EXPIRE_DAYS = 30


def generate_campaign_id():
    return "CP" + timezone.now().strftime("%Y%m%d") + get_random_string(6).upper()


def generate_campaign_winner_id():
    return "CW" + timezone.now().strftime("%Y%m%d%H%M%S") + get_random_string(5).upper()


def generate_campaign_redeem_code():
    return f"CG-{get_random_string(4).upper()}-{get_random_string(4).upper()}"


def default_campaign_winner_expire_at():
    return timezone.now() + timedelta(days=DEFAULT_CAMPAIGN_REDEEM_EXPIRE_DAYS)


class Campaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("published", "公開中"),
        ("closed", "已截止"),
        ("drawn", "已抽獎"),
        ("archived", "已封存"),
    ]

    campaign_id = models.CharField(
        max_length=40,
        unique=True,
        default=generate_campaign_id,
        verbose_name="活動抽獎編號",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="網址代稱",
        help_text="例如 guppy-summer-draw，網址會是 /campaigns/guppy-summer-draw/。",
    )
    campaign_name = models.CharField(max_length=120, verbose_name="活動抽獎名稱")
    campaign_desc = models.TextField(blank=True, verbose_name="活動說明")
    image_emoji = models.CharField(max_length=10, default="🎉", verbose_name="活動圖示")

    prize_name = models.CharField(max_length=120, verbose_name="獎品名稱")
    prize_desc = models.TextField(blank=True, verbose_name="獎品說明")
    winner_count = models.PositiveIntegerField(default=1, verbose_name="正取名額")
    alternate_count = models.PositiveIntegerField(default=0, verbose_name="候補名額")

    register_start_at = models.DateTimeField(verbose_name="報名開始時間")
    register_end_at = models.DateTimeField(verbose_name="報名截止時間")
    draw_at = models.DateTimeField(null=True, blank=True, verbose_name="預計抽獎時間")
    draw_executed_at = models.DateTimeField(null=True, blank=True, verbose_name="實際抽獎時間")

    eligibility_rule = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="資格說明",
        help_text="例如：限嘎比嘎比會員、限完成消費集點會員等。第一版先做文字說明。",
    )
    redeem_expire_days = models.PositiveIntegerField(
        default=DEFAULT_CAMPAIGN_REDEEM_EXPIRE_DAYS,
        verbose_name="中獎兌換有效天數",
    )
    notes = models.TextField(blank=True, verbose_name="內部備註")
    auto_draw = models.BooleanField(default=False, verbose_name="是否自動抽獎")
    publish_flag = models.BooleanField(default=True, verbose_name="是否公開顯示")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="狀態",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_campaigns",
        verbose_name="建立人員",
    )
    created_by_name = models.CharField(max_length=100, blank=True, verbose_name="建立人員名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ["-register_start_at", "-id"]
        verbose_name = "活動抽獎"
        verbose_name_plural = "活動抽獎"

    def __str__(self):
        return self.campaign_name

    def get_absolute_url(self):
        return reverse("campaign_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.publish_flag and self.status in {"published", "closed", "drawn"}

    @property
    def registration_is_open(self):
        now = timezone.now()
        return (
            self.publish_flag
            and self.status == "published"
            and self.register_start_at <= now <= self.register_end_at
        )

    @property
    def registration_count(self):
        return self.registrations.filter(status="registered").count()

    @property
    def primary_winner_count(self):
        return self.winners.filter(winner_type="primary").count()

    @property
    def alternate_winner_count(self):
        return self.winners.filter(winner_type="alternate").count()

    @property
    def is_drawn(self):
        return self.draw_executed_at is not None or self.status == "drawn"


class CampaignRegistration(models.Model):
    STATUS_CHOICES = [
        ("registered", "已報名"),
        ("cancelled", "已取消"),
    ]

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="活動抽獎",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaign_registrations",
        verbose_name="會員",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="registered",
        verbose_name="報名狀態",
    )
    register_time = models.DateTimeField(default=timezone.now, verbose_name="報名時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        ordering = ["-register_time"]
        constraints = [
            models.UniqueConstraint(fields=["campaign", "user"], name="unique_campaign_registration"),
        ]
        verbose_name = "活動抽獎報名"
        verbose_name_plural = "活動抽獎報名"

    def __str__(self):
        return f"{self.campaign} - {self.user}"


class CampaignWinner(models.Model):
    WINNER_TYPE_CHOICES = [
        ("primary", "正取"),
        ("alternate", "候補"),
    ]

    WINNER_STATUS_CHOICES = [
        ("unredeemed", "未兌換"),
        ("redeemed", "已兌換"),
        ("expired", "已過期"),
        ("void", "已作廢"),
    ]

    winner_id = models.CharField(
        max_length=50,
        unique=True,
        default=generate_campaign_winner_id,
        verbose_name="中獎編號",
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="winners",
        verbose_name="活動抽獎",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaign_winners",
        verbose_name="中獎會員",
    )
    campaign_name = models.CharField(max_length=120, verbose_name="活動名稱快照")
    prize_name = models.CharField(max_length=120, verbose_name="獎品名稱快照")
    prize_desc = models.TextField(blank=True, verbose_name="獎品說明快照")
    winner_type = models.CharField(
        max_length=20,
        choices=WINNER_TYPE_CHOICES,
        default="primary",
        verbose_name="中獎類型",
    )
    winner_rank = models.PositiveIntegerField(default=1, verbose_name="順位")
    winner_status = models.CharField(
        max_length=20,
        choices=WINNER_STATUS_CHOICES,
        default="unredeemed",
        verbose_name="兌換狀態",
    )
    draw_time = models.DateTimeField(default=timezone.now, verbose_name="抽獎時間")
    promoted_at = models.DateTimeField(null=True, blank=True, verbose_name="候補遞補時間")
    redeem_code = models.CharField(
        max_length=50,
        unique=True,
        default=generate_campaign_redeem_code,
        verbose_name="兌換碼",
    )
    redeem_qr_payload = models.TextField(blank=True, verbose_name="兌換 QR 內容")
    redeemed_at = models.DateTimeField(null=True, blank=True, verbose_name="兌換時間")
    redeemed_by = models.CharField(max_length=100, blank=True, verbose_name="核銷人員")
    expire_at = models.DateTimeField(default=default_campaign_winner_expire_at, verbose_name="到期時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        ordering = ["campaign", "winner_type", "winner_rank"]
        constraints = [
            models.UniqueConstraint(fields=["campaign", "user"], name="unique_campaign_winner"),
        ]
        verbose_name = "活動抽獎中獎名單"
        verbose_name_plural = "活動抽獎中獎名單"

    def __str__(self):
        return f"{self.campaign_name} - {self.user} - {self.get_winner_type_display()}"

    @property
    def is_expired(self):
        return timezone.now() > self.expire_at

    @property
    def can_redeem(self):
        return self.winner_type == "primary" and self.winner_status == "unredeemed" and not self.is_expired
