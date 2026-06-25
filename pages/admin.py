from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .image_utils import apply_brand_watermark_to_image_field
from .models import NewsPost, Product, StoreInfo


class ProductAdminForm(forms.ModelForm):
    crop_x = forms.FloatField(required=False, widget=forms.HiddenInput)
    crop_y = forms.FloatField(required=False, widget=forms.HiddenInput)
    crop_w = forms.FloatField(required=False, widget=forms.HiddenInput)
    crop_h = forms.FloatField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Product
        fields = "__all__"


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
    form = ProductAdminForm
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
        (
            "商品圖片與價格",
            {
                "fields": (
                    "image",
                    "crop_x",
                    "crop_y",
                    "crop_w",
                    "crop_h",
                    "image_preview",
                    "price_label",
                ),
                "description": "上傳商品圖後，可在下方拖曳正方形裁切框；儲存時系統會裁成正方形、壓縮圖片，並套用嘎比嘎比孔雀魚浮水印。",
            },
        ),
        ("前台顯示", {"fields": ("status", "is_featured", "is_published", "sort_order")} ),
    )

    class Media:
        css = {"all": ("pages/admin/product_cropper.css",)}
        js = ("pages/admin/product_cropper.js",)

    @admin.display(description="圖片預覽")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "尚未上傳"
        return format_html(
            '<img src="{}" style="width: 72px; height: 72px; object-fit: cover; border-radius: 14px;" alt="" />',
            obj.image.url,
        )

    def save_model(self, request, obj, form, change):
        crop_box = {
            "x": form.cleaned_data.get("crop_x"),
            "y": form.cleaned_data.get("crop_y"),
            "w": form.cleaned_data.get("crop_w"),
            "h": form.cleaned_data.get("crop_h"),
        }
        if all(value is not None for value in crop_box.values()):
            obj._product_crop_box = crop_box
        super().save_model(request, obj, form, change)

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
