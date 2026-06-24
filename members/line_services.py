import base64
import hashlib
import hmac
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.urls import reverse

from .models import MemberProfile

logger = logging.getLogger(__name__)

LINE_AUTHORIZE_URL = "https://access.line.me/oauth2/v2.1/authorize"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
LINE_PROFILE_URL = "https://api.line.me/v2/profile"
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


@dataclass
class LineApiResult:
    ok: bool
    status_code: int | None = None
    data: dict[str, Any] | None = None
    error: str = ""


def line_login_configured() -> bool:
    return bool(settings.LINE_LOGIN_CHANNEL_ID and settings.LINE_LOGIN_CHANNEL_SECRET)


def line_messaging_configured() -> bool:
    return bool(settings.LINE_MESSAGING_CHANNEL_ACCESS_TOKEN)


def get_site_url(request=None) -> str:
    configured_site_url = getattr(settings, "SITE_URL", "").strip().rstrip("/")

    if configured_site_url:
        return configured_site_url

    if request is not None:
        return f"{request.scheme}://{request.get_host()}"

    return ""


def build_line_callback_uri(request=None) -> str:
    return f"{get_site_url(request)}{reverse('line_callback')}"


def build_line_authorize_url(request, state: str, nonce: str) -> str:
    redirect_uri = build_line_callback_uri(request)
    params = {
        "response_type": "code",
        "client_id": settings.LINE_LOGIN_CHANNEL_ID,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": "profile openid",
        "nonce": nonce,
    }

    bot_prompt = getattr(settings, "LINE_LOGIN_BOT_PROMPT", "").strip()
    if bot_prompt:
        params["bot_prompt"] = bot_prompt

    return f"{LINE_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def _request_json(url: str, *, method: str = "GET", headers=None, data=None, timeout: int = 10) -> LineApiResult:
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
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            return LineApiResult(ok=True, status_code=response.status, data=parsed)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        logger.warning("LINE API HTTP error %s: %s", exc.code, error_body)
        return LineApiResult(ok=False, status_code=exc.code, error=error_body)
    except Exception as exc:
        logger.exception("LINE API request failed: %s", exc)
        return LineApiResult(ok=False, error=str(exc))


def exchange_code_for_token(code: str, redirect_uri: str) -> LineApiResult:
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


def fetch_line_profile(access_token: str) -> LineApiResult:
    return _request_json(
        LINE_PROFILE_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )


def verify_line_webhook_signature(body: bytes, signature: str) -> bool:
    channel_secret = settings.LINE_WEBHOOK_CHANNEL_SECRET

    if not channel_secret:
        # Local development convenience. In production, set LINE_WEBHOOK_CHANNEL_SECRET.
        return True

    digest = hmac.new(
        channel_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected_signature = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected_signature, signature or "")


def _line_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.LINE_MESSAGING_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def push_line_message(line_user_id: str, text: str) -> bool:
    if not line_messaging_configured() or not line_user_id:
        return False

    payload = {
        "to": line_user_id,
        "messages": [
            {
                "type": "text",
                "text": text[:4900],
            }
        ],
    }
    result = _request_json(LINE_PUSH_URL, method="POST", headers=_line_headers(), data=payload)
    return result.ok


def push_line_to_user(user, text: str) -> bool:
    try:
        profile = user.member_profile
    except MemberProfile.DoesNotExist:
        return False

    if not profile.line_user_id or not profile.line_notify_enabled:
        return False

    return push_line_message(profile.line_user_id, text)


def reply_line_message(reply_token: str, text: str) -> bool:
    if not line_messaging_configured() or not reply_token:
        return False

    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text[:4900],
            }
        ],
    }
    result = _request_json(LINE_REPLY_URL, method="POST", headers=_line_headers(), data=payload)
    return result.ok


def build_line_member_summary(line_user_id: str) -> str:
    profile = (
        MemberProfile.objects
        .select_related("user")
        .filter(line_user_id=line_user_id)
        .first()
    )

    if not profile:
        site_url = getattr(settings, "SITE_URL", "").strip().rstrip("/")
        bind_hint = f"\n會員中心：{site_url}/login/" if site_url else ""
        return (
            "尚未綁定嘎比嘎比孔雀魚會員帳號。\n"
            "請先登入會員網站，進入「LINE 綁定」完成綁定。"
            f"{bind_hint}"
        )

    user = profile.user
    display_name = user.first_name or user.email or user.username
    return (
        "嘎比嘎比孔雀魚會員資訊\n"
        f"會員：{display_name}\n"
        f"會員編號：{profile.member_no}\n"
        f"目前點數：{profile.points} 點\n"
        f"會員等級：{profile.get_level_display()}\n"
        "\n可輸入「獎品」查詢我的抽獎獎品，或輸入「活動」查看活動抽獎資訊。"
    )


def build_line_prize_summary(line_user_id: str) -> str:
    profile = MemberProfile.objects.select_related("user").filter(line_user_id=line_user_id).first()
    if not profile:
        return "尚未綁定會員帳號，請先到會員網站完成 LINE 綁定。"

    from lottery.models import LotterySpin

    spins = LotterySpin.objects.filter(
        user=profile.user,
        coupon_status="unredeemed",
    ).order_by("expire_at")[:5]

    if not spins:
        return "目前沒有可兌換的一般抽獎獎品。"

    lines = ["我的一般抽獎獎品"]
    for spin in spins:
        lines.append(f"- {spin.prize_name}｜兌換碼 {spin.redeem_code}｜到期 {spin.expire_at:%Y/%m/%d}")
    return "\n".join(lines)


def build_line_campaign_summary(line_user_id: str) -> str:
    profile = MemberProfile.objects.select_related("user").filter(line_user_id=line_user_id).first()
    if not profile:
        return "尚未綁定會員帳號，請先到會員網站完成 LINE 綁定。"

    from campaigns.models import CampaignWinner

    winners = CampaignWinner.objects.filter(
        user=profile.user,
        winner_status="unredeemed",
    ).order_by("expire_at")[:5]

    if not winners:
        return "目前沒有可兌換的活動抽獎獎品。"

    lines = ["我的活動抽獎獎品"]
    for winner in winners:
        label = "正取" if winner.winner_type == "primary" else "候補"
        lines.append(f"- {winner.campaign_name}｜{label}｜{winner.prize_name}｜兌換碼 {winner.redeem_code}")
    return "\n".join(lines)


def build_line_auto_reply(line_user_id: str, text: str) -> str:
    text = (text or "").strip().lower()

    if any(keyword in text for keyword in ["點數", "會員", "查詢", "point", "points"]):
        return build_line_member_summary(line_user_id)

    if any(keyword in text for keyword in ["獎品", "兌換", "抽獎", "prize"]):
        return build_line_prize_summary(line_user_id)

    if any(keyword in text for keyword in ["活動", "campaign"]):
        return build_line_campaign_summary(line_user_id)

    return (
        "嗨，這裡是嘎比嘎比孔雀魚會員小幫手 🐠\n"
        "你可以輸入：\n"
        "1. 點數｜查詢會員點數\n"
        "2. 獎品｜查詢一般抽獎獎品\n"
        "3. 活動｜查詢活動抽獎獎品"
    )
