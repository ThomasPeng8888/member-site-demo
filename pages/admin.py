from django.contrib import admin
from django.utils.html import format_html

from .models import NewsPost, Product, StoreInfo


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_pinned",
        "is_published",
        "published_at",
        "updated_at",
    )
    list_filter = ("category", "is_pinned", "is_published", "published_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    fieldsets = (
        ("內容", {"fields": ("title", "slug", "category", "cover_emoji", "summary", "content")} ),
        ("發布設定", {"fields": ("is_pinned", "is_published", "published_at")} ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "price_label",
        "is_featured",
        "is_published",
        "sort_order",
        "image_preview",
    )
    list_filter = ("category", "status", "is_featured", "is_published")
    search_fields = ("title", "short_description", "description", "price_label")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("status", "is_featured", "is_published", "sort_order")
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("基本資料", {"fields": ("title", "slug", "category", "short_description", "description")} ),
        ("商品圖片與價格", {"fields": ("image", "image_preview", "price_label")} ),
        ("前台顯示", {"fields": ("status", "is_featured", "is_published", "sort_order")} ),
    )

    @admin.display(description="圖片預覽")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "尚未上傳"
        return format_html(
            '<img src="{}" style="width: 72px; height: 72px; object-fit: cover; border-radius: 14px;" alt="" />',
            obj.image.url,
        )


@admin.register(StoreInfo)
class StoreInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "is_primary", "is_published", "sort_order", "updated_at")
    list_filter = ("is_primary", "is_published")
    search_fields = ("name", "tagline", "intro", "address", "phone")
    list_editable = ("is_primary", "is_published", "sort_order")
    fieldsets = (
        ("店鋪介紹", {"fields": ("name", "tagline", "intro", "note")} ),
        ("聯絡資訊", {"fields": ("address", "business_hours", "phone", "line_url", "facebook_url", "google_map_url")} ),
        ("前台顯示", {"fields": ("is_primary", "is_published", "sort_order")} ),
    )
