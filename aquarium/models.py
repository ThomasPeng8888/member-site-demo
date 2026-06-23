from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string


def generate_ticket_no():
    return "TK" + get_random_string(10).upper()


class Activity(models.Model):
    CATEGORY_CHOICES = [
        ("show", "表演活動"),
        ("class", "體驗課程"),
        ("event", "特別活動"),
        ("conservation", "保育教育"),
    ]

    title = models.CharField(max_length=100, verbose_name="活動名稱")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="網址代稱")
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="event",
        verbose_name="活動類型",
    )
    summary = models.CharField(max_length=180, verbose_name="活動摘要")
    description = models.TextField(verbose_name="活動說明")
    image_emoji = models.CharField(
        max_length=10,
        default="🐬",
        verbose_name="活動圖示",
    )
    starts_at = models.DateTimeField(verbose_name="開始時間")
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name="結束時間")
    location = models.CharField(max_length=100, default="主展區", verbose_name="地點")
    points_reward = models.PositiveIntegerField(default=0, verbose_name="報名獲得點數")
    max_capacity = models.PositiveIntegerField(default=0, verbose_name="人數上限，0 表示不限")
    is_published = models.BooleanField(default=True, verbose_name="是否公開")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        ordering = ["starts_at"]
        verbose_name = "水族館活動"
        verbose_name_plural = "水族館活動"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("activity_detail", kwargs={"slug": self.slug})

    @property
    def registration_count(self):
        return self.registrations.count()

    @property
    def has_capacity(self):
        if self.max_capacity == 0:
            return True
        return self.registration_count < self.max_capacity

    @property
    def is_upcoming(self):
        return self.starts_at >= timezone.now()


class ActivityRegistration(models.Model):
    STATUS_CHOICES = [
        ("registered", "已報名"),
        ("cancelled", "已取消"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_registrations",
        verbose_name="會員",
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="活動",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="registered",
        verbose_name="狀態",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="報名時間")

    class Meta:
        unique_together = ("user", "activity")
        ordering = ["-created_at"]
        verbose_name = "活動報名"
        verbose_name_plural = "活動報名"

    def __str__(self):
        return f"{self.user} - {self.activity}"


class MemberTicket(models.Model):
    TICKET_TYPE_CHOICES = [
        ("general", "一般入場券"),
        ("child", "兒童票"),
        ("event", "活動票"),
        ("gift", "贈品券"),
    ]

    STATUS_CHOICES = [
        ("available", "可使用"),
        ("used", "已使用"),
        ("expired", "已過期"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_tickets",
        verbose_name="會員",
    )
    ticket_no = models.CharField(
        max_length=30,
        unique=True,
        default=generate_ticket_no,
        verbose_name="票券編號",
    )
    title = models.CharField(max_length=100, verbose_name="票券名稱")
    ticket_type = models.CharField(
        max_length=30,
        choices=TICKET_TYPE_CHOICES,
        default="general",
        verbose_name="票券類型",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
        verbose_name="狀態",
    )
    valid_until = models.DateField(null=True, blank=True, verbose_name="有效期限")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="使用時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "會員票券"
        verbose_name_plural = "會員票券"

    def __str__(self):
        return f"{self.ticket_no} - {self.title}"

    @property
    def is_valid(self):
        if self.status != "available":
            return False
        if self.valid_until and self.valid_until < timezone.localdate():
            return False
        return True


class PointTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("earn", "獲得點數"),
        ("spend", "使用點數"),
        ("adjust", "人工調整"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions",
        verbose_name="會員",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name="交易類型",
    )
    points = models.PositiveIntegerField(verbose_name="點數")
    title = models.CharField(max_length=120, verbose_name="紀錄標題")
    note = models.TextField(blank=True, verbose_name="備註")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "點數紀錄"
        verbose_name_plural = "點數紀錄"

    def __str__(self):
        return f"{self.user} - {self.get_transaction_type_display()} {self.points}"