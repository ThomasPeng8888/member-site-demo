from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string


LOTTERY_COST_POINTS = 10
REGULAR_COUPON_EXPIRE_DAYS = 90


def generate_spin_code():
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    return f"SP{timestamp}{get_random_string(6).upper()}"


def generate_redeem_code():
    return f"GP-{get_random_string(4).upper()}-{get_random_string(4).upper()}"

def default_regular_coupon_expire_at():
    return timezone.now() + timedelta(days=REGULAR_COUPON_EXPIRE_DAYS)


class LotteryPrize(models.Model):
    prize_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="獎項代碼",
    )
    prize_name = models.CharField(
        max_length=100,
        verbose_name="獎項名稱",
    )
    prize_desc = models.TextField(
        blank=True,
        verbose_name="獎項說明",
    )
    image_emoji = models.CharField(
        max_length=10,
        default="🎁",
        verbose_name="獎項圖示",
    )
    weight = models.PositiveIntegerField(
        default=1,
        verbose_name="抽中權重",
        help_text="數字越大越容易抽中。",
    )
    stock = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="庫存",
        help_text="空白代表無限庫存；0 代表不可抽。",
    )
    points_cost = models.PositiveIntegerField(
        default=LOTTERY_COST_POINTS,
        verbose_name="消耗點數",
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name="是否啟用",
    )
    start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="開始時間",
    )
    end_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="結束時間",
    )
    sort_order = models.PositiveIntegerField(
        default=999,
        verbose_name="排序",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="建立時間",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新時間",
    )

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "常態抽獎獎項"
        verbose_name_plural = "常態抽獎獎項"

    def __str__(self):
        return self.prize_name

    @property
    def is_available(self):
        now = timezone.now()

        if not self.enabled:
            return False

        if self.start_at and self.start_at > now:
            return False

        if self.end_at and self.end_at < now:
            return False

        if self.stock is not None and self.stock <= 0:
            return False

        return True


class LotterySpin(models.Model):
    COUPON_STATUS_CHOICES = [
        ("unredeemed", "未兌換"),
        ("redeemed", "已兌換"),
        ("expired", "已過期"),
        ("void", "已作廢"),
    ]

    RESULT_STATUS_CHOICES = [
        ("success", "成功"),
        ("failed", "失敗"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lottery_spins",
        verbose_name="會員",
    )
    spin_code = models.CharField(
        max_length=50,
        unique=True,
        default=generate_spin_code,
        verbose_name="抽獎編號",
    )
    spin_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="抽獎時間",
    )
    cost_points = models.PositiveIntegerField(
        default=LOTTERY_COST_POINTS,
        verbose_name="消耗點數",
    )
    prize = models.ForeignKey(
        LotteryPrize,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="spins",
        verbose_name="抽中獎項",
    )
    prize_name = models.CharField(
        max_length=100,
        verbose_name="獎項名稱快照",
    )
    stock_before = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="抽獎前庫存",
    )
    stock_after = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="抽獎後庫存",
    )
    balance_after = models.PositiveIntegerField(
        default=0,
        verbose_name="抽獎後點數",
    )
    result_status = models.CharField(
        max_length=20,
        choices=RESULT_STATUS_CHOICES,
        default="success",
        verbose_name="抽獎結果",
    )
    coupon_status = models.CharField(
        max_length=20,
        choices=COUPON_STATUS_CHOICES,
        default="unredeemed",
        verbose_name="兌換狀態",
    )
    redeem_code = models.CharField(
        max_length=50,
        unique=True,
        default=generate_redeem_code,
        verbose_name="兌換碼",
    )
    redeem_qr_payload = models.TextField(
        blank=True,
        verbose_name="兌換 QR 內容",
    )
    redeemed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="兌換時間",
    )
    redeemed_by = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="核銷人員",
    )
    expire_at = models.DateTimeField(
        default=default_regular_coupon_expire_at,
        verbose_name="到期時間",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="建立時間",
    )

    class Meta:
        ordering = ["-spin_time"]
        verbose_name = "常態抽獎紀錄"
        verbose_name_plural = "常態抽獎紀錄"

    def __str__(self):
        return f"{self.spin_code} - {self.prize_name}"

    @property
    def is_expired(self):
        return timezone.now() > self.expire_at

    @property
    def can_redeem(self):
        return self.coupon_status == "unredeemed" and not self.is_expired

    def get_absolute_url(self):
        return reverse("my_prizes")