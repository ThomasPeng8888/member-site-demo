from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string


def generate_member_no():
    return "AQ" + get_random_string(8).upper()


class MemberProfile(models.Model):
    LEVEL_CHOICES = [
        ("basic", "Basic"),
        ("silver", "Silver"),
        ("gold", "Gold"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    member_no = models.CharField(
        max_length=20,
        unique=True,
        default=generate_member_no,
        verbose_name="會員編號",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="手機",
    )
    points = models.PositiveIntegerField(
        default=0,
        verbose_name="會員點數",
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default="basic",
        verbose_name="會員等級",
    )
    line_user_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="LINE User ID",
    )
    line_display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="LINE 顯示名稱",
    )
    line_picture_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="LINE 頭像網址",
    )
    line_bound_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="LINE 綁定時間",
    )
    line_notify_enabled = models.BooleanField(
        default=True,
        verbose_name="啟用 LINE 通知",
    )
    google_sub = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="Google 帳號識別碼",
    )
    google_email = models.EmailField(
        blank=True,
        verbose_name="Google Email",
    )
    google_bound_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Google 綁定時間",
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
        constraints = [
            models.UniqueConstraint(
                fields=["line_user_id"],
                condition=~Q(line_user_id=""),
                name="unique_non_empty_line_user_id",
            ),
            models.UniqueConstraint(
                fields=["google_sub"],
                condition=~Q(google_sub=""),
                name="unique_non_empty_google_sub",
            ),
        ]
        verbose_name = "會員資料"
        verbose_name_plural = "會員資料"

    def __str__(self):
        return f"{self.member_no} - {self.user.email or self.user.username}"

    @property
    def is_line_bound(self):
        return bool(self.line_user_id)

    @property
    def is_google_bound(self):
        return bool(self.google_sub)
