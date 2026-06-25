from django.contrib import admin
from django.utils.html import format_html

from .image_utils import apply_brand_watermark_to_image_field
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
    actions = ("apply_watermark_to_selected",)
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

    @admin.action(description="重新套用嘎比嘎比孔雀魚浮水印")
    def apply_watermark_to_selected(self, request, queryset):
        total = 0
        skipped = 0

        for product in queryset:
            if not product.image:
                skipped += 1
                continue

            image_name_changed = apply_brand_watermark_to_image_field(product.image)
            if image_name_changed:
                Product.objects.filter(pk=product.pk).update(image=product.image.name)
            total += 1

        if total:
            self.message_user(request, f"已處理 {total} 張商品圖片浮水印。")
        if skipped:
            self.message_user(request, f"另有 {skipped} 個商品尚未上傳圖片，已略過。")


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
