from django.db import models
from django.urls import reverse
from django.utils import timezone


class NewsPost(models.Model):
    CATEGORY_CHOICES = [
        ("news", "最新消息"),
        ("arrival", "新品到貨"),
        ("care", "飼育知識"),
        ("event", "活動公告"),
        ("store", "店鋪公告"),
    ]

    title = models.CharField(max_length=120, verbose_name="消息標題")
    slug = models.SlugField(max_length=140, unique=True, verbose_name="網址代稱")
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="news",
        verbose_name="消息分類",
    )
    summary = models.CharField(max_length=220, verbose_name="消息摘要")
    content = models.TextField(verbose_name="消息內容")
    cover_emoji = models.CharField(
        max_length=12,
        default="🐟",
        verbose_name="列表圖示",
        help_text="前台卡片使用的小圖示，例如 🐟、✨、📣。",
    )
    is_pinned = models.BooleanField(default=False, verbose_name="是否置頂")
    is_published = models.BooleanField(default=True, verbose_name="是否公開")
    published_at = models.DateTimeField(default=timezone.now, verbose_name="發布時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ["-is_pinned", "-published_at", "-id"]
        verbose_name = "最新消息"
        verbose_name_plural = "最新消息"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news_detail", kwargs={"slug": self.slug})

    @property
    def is_visible(self):
        return self.is_published and self.published_at <= timezone.now()


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("guppy", "孔雀魚"),
        ("feed", "飼料與營養"),
        ("equipment", "水族用品"),
        ("service", "服務與套組"),
        ("other", "其他商品"),
    ]

    STATUS_CHOICES = [
        ("available", "販售中"),
        ("limited", "限量 / 預約"),
        ("sold_out", "暫售完"),
        ("hidden", "不顯示"),
    ]

    title = models.CharField(max_length=120, verbose_name="商品名稱")
    slug = models.SlugField(max_length=140, unique=True, verbose_name="網址代稱")
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="guppy",
        verbose_name="商品分類",
    )
    short_description = models.CharField(max_length=220, verbose_name="商品簡介")
    description = models.TextField(verbose_name="商品說明")
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        verbose_name="商品圖片",
        help_text="目前前台先顯示一張主圖。後台會提供正方形裁切工具，系統會自動壓縮為適合網頁瀏覽的大小，並加入淡淡品牌浮水印。",
    )
    price_label = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="價格文字",
        help_text="例如：現場洽詢、NT$ 350、依尺寸報價。",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="available",
        verbose_name="商品狀態",
    )
    is_featured = models.BooleanField(default=False, verbose_name="首頁精選")
    show_on_homepage = models.BooleanField(
        default=False,
        verbose_name="顯示於首頁輪播",
        help_text="勾選後會優先出現在首頁上方商品照片輪播，可用首頁輪播排序控制順序。",
    )
    homepage_order = models.PositiveIntegerField(
        default=0,
        verbose_name="首頁輪播排序",
        help_text="數字越小越前面；只影響首頁輪播，不影響商品列表排序。",
    )
    is_published = models.BooleanField(default=True, verbose_name="是否公開")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="商品列表排序，數字越小越前面")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ["sort_order", "-is_featured", "-created_at", "-id"]
        verbose_name = "商品"
        verbose_name_plural = "商品資訊"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        should_watermark = bool(self.image)

        if self.pk:
            previous_image = (
                Product.objects.filter(pk=self.pk)
                .values_list("image", flat=True)
                .first()
            )
            should_watermark = bool(self.image) and self.image.name != previous_image

        super().save(*args, **kwargs)

        if should_watermark and self.image:
            from .image_utils import apply_brand_watermark_to_image_field

            crop_box = getattr(self, "_product_crop_box", None)
            image_name_changed = apply_brand_watermark_to_image_field(self.image, crop_box=crop_box)
            if image_name_changed and self.pk:
                type(self).objects.filter(pk=self.pk).update(image=self.image.name)

    @property
    def is_visible(self):
        return self.is_published and self.status != "hidden"


class StoreInfo(models.Model):
    name = models.CharField(max_length=120, default="嘎比嘎比孔雀魚", verbose_name="店鋪名稱")
    tagline = models.CharField(
        max_length=160,
        blank=True,
        default="專注孔雀魚選育、交流與會員服務的水族工作室。",
        verbose_name="店鋪短標語",
    )
    intro = models.TextField(verbose_name="店鋪介紹")
    address = models.CharField(max_length=220, blank=True, verbose_name="地址")
    business_hours = models.TextField(blank=True, verbose_name="營業時間")
    phone = models.CharField(max_length=60, blank=True, verbose_name="聯絡電話")
    line_url = models.URLField(blank=True, verbose_name="LINE 官方帳號網址")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook / 社群網址")
    google_map_url = models.URLField(blank=True, verbose_name="Google Map 連結")
    note = models.TextField(blank=True, verbose_name="到店提醒 / 補充說明")
    is_primary = models.BooleanField(default=False, verbose_name="主要店鋪")
    is_published = models.BooleanField(default=True, verbose_name="是否公開")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="排序，數字越小越前面")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        ordering = ["sort_order", "-is_primary", "name"]
        verbose_name = "店鋪資訊"
        verbose_name_plural = "店鋪資訊"

    def __str__(self):
        return self.name
