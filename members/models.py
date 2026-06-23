from django.conf import settings
from django.db import models
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
        verbose_name="LINE User ID",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="建立時間",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新時間",
    )

    def __str__(self):
        return f"{self.member_no} - {self.user.email or self.user.username}"