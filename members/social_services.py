import json
import logging
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.urls import reverse

from .line_services import get_site_url

logger = logging.getLogger(__name__)

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

LINE_AUTHORIZE_URL = "https://access.line.me/oauth2/v2.1/authorize"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
LINE_PROFILE_URL = "https://api.line.me/v2/profile"

def _build_oauth_ssl_context() -> ssl.SSLContext:
    """
    Python 3.13+ / 3.14 本機開發時，有些環境會因較嚴格的 X.509 憑證檢查
    出現 Missing Authority Key Identifier。

    這裡仍保留 SSL 憑證驗證，只移除 VERIFY_X509_STRICT。
    不要改成 ssl._create_unverified_context()，那會關閉憑證驗證。
    """
    context = ssl.create_default_context()

    if hasattr(ssl, "VERIFY_X509_STRICT"):
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT

    return context

@dataclass
class OAuthResult:
    ok: bool
    status_code: int | None = None
    data: dict[str, Any] | None = None
    error: str = ""


def google_login_configured() -> bool:
    return bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)


def line_social_login_configured() -> bool:
    return bool(settings.LINE_LOGIN_CHANNEL_ID and settings.LINE_LOGIN_CHANNEL_SECRET)


def build_google_callback_uri(request=None) -> str:
    return f"{get_site_url(request)}{reverse('social_google_callback')}"


def build_line_social_callback_uri(request=None) -> str:
    return f"{get_site_url(request)}{reverse('social_line_callback')}"


def build_google_authorize_url(request, *, state: str) -> str:
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": build_google_callback_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def build_line_social_authorize_url(request, *, state: str, nonce: str) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.LINE_LOGIN_CHANNEL_ID,
        "redirect_uri": build_line_social_callback_uri(request),
        "state": state,
        "scope": "profile openid",
        "nonce": nonce,
    }

    bot_prompt = getattr(settings, "LINE_LOGIN_BOT_PROMPT", "").strip()
    if bot_prompt:
        params["bot_prompt"] = bot_prompt

    return f"{LINE_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def _request_json(url: str, *, method: str = "GET", headers=None, data=None, timeout: int = 10) -> OAuthResult:
    headers = headers or {}
    body = None

    if data is not None:
        if isinstance(data, bytes):
            body = data
        else:
            body = json.dumps(data).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        ssl_context = _build_oauth_ssl_context()

        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            return OAuthResult(ok=True, status_code=response.status, data=parsed)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        logger.warning("OAuth HTTP error %s from %s: %s", exc.code, url, error_body)
        return OAuthResult(ok=False, status_code=exc.code, error=error_body)
    except Exception as exc:
        logger.exception("OAuth request failed: %s", exc)
        return OAuthResult(ok=False, error=str(exc))


def exchange_google_code(code: str, redirect_uri: str) -> OAuthResult:
    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    return _request_json(
        GOOGLE_TOKEN_URL,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
    )


def fetch_google_userinfo(access_token: str) -> OAuthResult:
    return _request_json(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )


def exchange_line_social_code(code: str, redirect_uri: str) -> OAuthResult:
    payload = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.LINE_LOGIN_CHANNEL_ID,
            "client_secret": settings.LINE_LOGIN_CHANNEL_SECRET,
        }
    ).encode("utf-8")

    return _request_json(
        LINE_TOKEN_URL,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
    )


def fetch_line_social_profile(access_token: str) -> OAuthResult:
    return _request_json(
        LINE_PROFILE_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
