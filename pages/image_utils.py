"""Image helpers for official site content.

Product photos should keep their original visual quality, but uploaded images can
still receive a subtle brand watermark to reduce casual image reuse.
"""
from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageEnhance, ImageOps

logger = logging.getLogger(__name__)

WATERMARK_ASSET = (
    Path(settings.BASE_DIR)
    / "pages"
    / "static"
    / "pages"
    / "images"
    / "gabi-watermark-text.png"
)

JPEG_SUFFIXES = {".jpg", ".jpeg"}
WEBP_SUFFIXES = {".webp"}


def _resize_to_width(image: Image.Image, target_width: int) -> Image.Image:
    """Resize proportionally while keeping a reasonable minimum size."""
    target_width = max(80, int(target_width))
    if image.width == target_width:
        return image.copy()

    ratio = target_width / max(1, image.width)
    target_height = max(1, int(image.height * ratio))
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


def _apply_alpha(image: Image.Image, opacity: float) -> Image.Image:
    """Apply opacity to an RGBA image without changing its colors."""
    watermark = image.convert("RGBA")
    opacity = max(0.0, min(float(opacity), 1.0))
    alpha = watermark.getchannel("A")
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)
    return watermark


def _save_image_to_bytes(image: Image.Image, suffix: str) -> tuple[bytes, str]:
    """Save with web-friendly settings and return bytes plus format label."""
    suffix = suffix.lower()
    buffer = BytesIO()

    if suffix in JPEG_SUFFIXES:
        background = Image.new("RGB", image.size, "white")
        background.paste(image.convert("RGBA"), mask=image.convert("RGBA").getchannel("A"))
        background.save(buffer, format="JPEG", quality=92, optimize=True, progressive=True)
        return buffer.getvalue(), "JPEG"

    if suffix in WEBP_SUFFIXES:
        image.convert("RGBA").save(buffer, format="WEBP", quality=92, method=6)
        return buffer.getvalue(), "WEBP"

    image.convert("RGBA").save(buffer, format="PNG", optimize=True)
    return buffer.getvalue(), "PNG"


def apply_brand_watermark_to_image_field(image_field) -> bool:
    """Apply a subtle GabiGabi watermark to a Django ImageField file.

    The normal path overwrites the just-uploaded media file, so no database field
    needs to change. If a custom storage cannot overwrite in place, the function
    saves a new file name through the ImageField and returns True so the caller can
    persist the updated name.

    Returns:
        True when image_field.name changed and the model should be saved again.
        False when the image was overwritten in place or skipped safely.
    """
    if not image_field or not getattr(image_field, "name", ""):
        return False

    if not WATERMARK_ASSET.exists():
        logger.warning("Product watermark asset not found: %s", WATERMARK_ASSET)
        return False

    try:
        with image_field.storage.open(image_field.name, "rb") as source_file:
            original = Image.open(source_file)
            original = ImageOps.exif_transpose(original)
            base = original.convert("RGBA")
    except Exception:
        logger.exception("Unable to open product image for watermark: %s", image_field.name)
        return False

    width, height = base.size
    if width < 160 or height < 160:
        # Very small images are usually icons/thumbnails. Avoid making them busy.
        return False

    try:
        watermark_source = Image.open(WATERMARK_ASSET).convert("RGBA")
    except Exception:
        logger.exception("Unable to open watermark asset: %s", WATERMARK_ASSET)
        return False

    overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
    min_edge = min(width, height)

    # 1) Ultra-light centered diagonal text: discourages cropping while staying
    #    gentle enough that fish colors and patterns remain the visual focus.
    if min_edge >= 420:
        center_width = min(int(width * 0.62), int(height * 1.08), 900)
        center_mark = _resize_to_width(watermark_source, center_width)
        center_mark = _apply_alpha(center_mark, 0.075)
        center_mark = center_mark.rotate(-18, expand=True, resample=Image.Resampling.BICUBIC)
        center_position = ((width - center_mark.width) // 2, (height - center_mark.height) // 2)
        overlay.alpha_composite(center_mark, dest=center_position)

    # 2) Small bottom-right signature: clearer brand ownership, but with low
    #    opacity and margin so it does not cover the product subject.
    corner_width = min(max(int(width * 0.26), 150), 360)
    corner_mark = _resize_to_width(watermark_source, corner_width)
    corner_mark = _apply_alpha(corner_mark, 0.22)
    margin = max(16, int(min_edge * 0.035))
    corner_position = (
        max(margin, width - corner_mark.width - margin),
        max(margin, height - corner_mark.height - margin),
    )
    overlay.alpha_composite(corner_mark, dest=corner_position)

    watermarked = Image.alpha_composite(base, overlay)
    suffix = Path(image_field.name).suffix.lower() or ".jpg"
    output_bytes, _format = _save_image_to_bytes(watermarked, suffix)

    # Prefer overwriting the just-uploaded file. This keeps the model image path
    # stable and avoids orphaning an unwatermarked original file.
    try:
        with image_field.storage.open(image_field.name, "wb") as target_file:
            target_file.write(output_bytes)
        return False
    except Exception:
        logger.info("Storage does not support in-place overwrite; saving watermarked copy instead.")

    original_name = image_field.name
    image_field.save(original_name, ContentFile(output_bytes), save=False)
    return image_field.name != original_name
