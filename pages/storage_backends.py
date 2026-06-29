"""Custom storage backends for uploaded media."""
from __future__ import annotations

try:
    from storages.backends.s3 import S3Storage
except ImportError:  # pragma: no cover - compatibility with older django-storages
    from storages.backends.s3boto3 import S3Boto3Storage as S3Storage


class R2MediaStorage(S3Storage):
    """Store user-uploaded media in Cloudflare R2.

    Product images keep the same ImageField flow: admin upload -> square crop ->
    compression -> adaptive GuppyGuppy watermark -> R2 object storage.
    """

    location = "media"
    file_overwrite = True
    default_acl = None
    querystring_auth = False
