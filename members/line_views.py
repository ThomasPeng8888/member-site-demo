import json
import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .line_services import (
    build_line_authorize_url,
    build_line_auto_reply,
    build_line_callback_uri,
    exchange_code_for_token,
    fetch_line_profile,
    line_login_configured,
    push_line_to_user,
    reply_line_message,
    verify_line_webhook_signature,
)
from .models import MemberProfile


@login_required
def line_settings(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)

    return render(
        request,
        "members/line_settings.html",
        {
            "profile": profile,
            "line_login_configured": line_login_configured(),
            "callback_uri": build_line_callback_uri(request),
        },
    )


@login_required
def line_bind_start(request):
    if not line_login_configured():
        messages.error(request, "LINE Login 尚未設定，請先在 Render 設定 LINE_LOGIN_CHANNEL_ID 與 LINE_LOGIN_CHANNEL_SECRET。")
        return redirect("line_settings")

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    request.session["line_oauth_state"] = state
    request.session["line_oauth_nonce"] = nonce
    request.session["line_oauth_next"] = request.GET.get("next") or reverse("line_settings")

    return redirect(build_line_authorize_url(request, state=state, nonce=nonce))


@login_required
def line_callback(request):
    error = request.GET.get("error")
    if error:
        messages.error(request, f"LINE 綁定取消或失敗：{request.GET.get('error_description') or error}")
        return redirect("line_settings")

    code = request.GET.get("code")
    state = request.GET.get("state")
    session_state = request.session.get("line_oauth_state")

    if not code or not state or not session_state or state != session_state:
        messages.error(request, "LINE 綁定驗證失敗，請重新操作。")
        return redirect("line_settings")

    redirect_uri = build_line_callback_uri(request)
    token_result = exchange_code_for_token(code, redirect_uri)

    if not token_result.ok or not token_result.data or not token_result.data.get("access_token"):
        messages.error(request, "無法取得 LINE access token，請確認 LINE Login 設定與 callback URL。")
        return redirect("line_settings")

    profile_result = fetch_line_profile(token_result.data["access_token"])

    if not profile_result.ok or not profile_result.data or not profile_result.data.get("userId"):
        messages.error(request, "無法取得 LINE 使用者資料，請稍後再試。")
        return redirect("line_settings")

    line_profile = profile_result.data
    line_user_id = line_profile["userId"]

    with transaction.atomic():
        current_profile, _ = MemberProfile.objects.select_for_update().get_or_create(user=request.user)
        existing_profile = (
            MemberProfile.objects
            .select_for_update()
            .filter(line_user_id=line_user_id)
            .exclude(user=request.user)
            .first()
        )

        if existing_profile:
            messages.error(request, "這個 LINE 帳號已經綁定其他會員，請先解除原本綁定。")
            return redirect("line_settings")

        current_profile.line_user_id = line_user_id
        current_profile.line_display_name = line_profile.get("displayName", "")
        current_profile.line_picture_url = line_profile.get("pictureUrl", "")
        current_profile.line_bound_at = timezone.now()
        current_profile.line_notify_enabled = True
        current_profile.save(
            update_fields=[
                "line_user_id",
                "line_display_name",
                "line_picture_url",
                "line_bound_at",
                "line_notify_enabled",
                "updated_at",
            ]
        )

    request.session.pop("line_oauth_state", None)
    request.session.pop("line_oauth_nonce", None)
    next_url = request.session.pop("line_oauth_next", reverse("line_settings"))

    messages.success(request, "LINE 綁定成功！之後可透過 LINE 接收點數、抽獎與核銷通知。")
    push_line_to_user(
        request.user,
        "嘎比嘎比孔雀魚會員綁定成功 🐠\n之後你可以直接輸入「點數」「獎品」「活動」查詢會員資訊。",
    )
    return redirect(next_url)


@login_required
@require_POST
def line_unbind(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    profile.line_user_id = ""
    profile.line_display_name = ""
    profile.line_picture_url = ""
    profile.line_bound_at = None
    profile.line_notify_enabled = True
    profile.save(
        update_fields=[
            "line_user_id",
            "line_display_name",
            "line_picture_url",
            "line_bound_at",
            "line_notify_enabled",
            "updated_at",
        ]
    )
    messages.success(request, "已解除 LINE 綁定。")
    return redirect("line_settings")


@login_required
@require_POST
def line_toggle_notify(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)

    if not profile.line_user_id:
        messages.error(request, "尚未綁定 LINE，無法設定通知。")
        return redirect("line_settings")

    profile.line_notify_enabled = not profile.line_notify_enabled
    profile.save(update_fields=["line_notify_enabled", "updated_at"])

    if profile.line_notify_enabled:
        messages.success(request, "已開啟 LINE 通知。")
    else:
        messages.success(request, "已暫停 LINE 通知。")

    return redirect("line_settings")


@csrf_exempt
@require_POST
def line_webhook(request):
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_line_webhook_signature(request.body, signature):
        return HttpResponseForbidden("Invalid signature")

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    for event in payload.get("events", []):
        if event.get("type") != "message":
            continue

        message = event.get("message", {})
        if message.get("type") != "text":
            continue

        source = event.get("source", {})
        line_user_id = source.get("userId", "")
        reply_token = event.get("replyToken", "")
        reply_text = build_line_auto_reply(line_user_id, message.get("text", ""))
        reply_line_message(reply_token, reply_text)

    return JsonResponse({"ok": True})
