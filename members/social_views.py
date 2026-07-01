import secrets
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from aquarium.models import PointTransaction

from .forms import SocialEmailCompleteForm
from .models import MemberProfile
from .social_services import (
    build_google_authorize_url,
    build_google_callback_uri,
    build_line_social_authorize_url,
    build_line_social_callback_uri,
    exchange_google_code,
    exchange_line_social_code,
    fetch_google_userinfo,
    fetch_line_social_profile,
    google_login_configured,
    line_social_login_configured,
)


PENDING_LINE_SESSION_KEY = "social_line_pending_profile"


def _safe_next_url(value: str | None) -> str:
    if not value:
        return reverse("dashboard")
    parsed = urlparse(value)
    if parsed.netloc or parsed.scheme:
        return reverse("dashboard")
    if not value.startswith("/"):
        return reverse("dashboard")
    return value


def _create_social_member(email: str, *, first_name: str = "", phone: str = "") -> User:
    user = User(username=email, email=email, first_name=(first_name or "").strip())
    user.set_unusable_password()
    user.save()

    MemberProfile.objects.create(
        user=user,
        phone=(phone or "").strip(),
        points=100,
    )
    PointTransaction.objects.create(
        user=user,
        transaction_type="earn",
        points=100,
        title="新會員註冊禮",
        note="透過社群快速登入加入嘎比嘎比孔雀魚會員中心，自動獲得 100 點。",
    )
    return user


def _find_user_by_email(email: str) -> User | None:
    normalized_email = email.strip().lower()
    return (
        User.objects.filter(email__iexact=normalized_email).first()
        or User.objects.filter(username__iexact=normalized_email).first()
    )


def _get_or_create_user_by_email(email: str, *, first_name: str = "", phone: str = "") -> tuple[User, bool]:
    normalized_email = email.strip().lower()
    user = _find_user_by_email(normalized_email)
    if user:
        changed_fields = []
        if not user.email:
            user.email = normalized_email
            changed_fields.append("email")
        if not user.first_name and first_name:
            user.first_name = first_name.strip()
            changed_fields.append("first_name")
        if changed_fields:
            user.save(update_fields=changed_fields)
        MemberProfile.objects.get_or_create(user=user)
        return user, False

    return _create_social_member(normalized_email, first_name=first_name, phone=phone), True


def social_google_start(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if not google_login_configured():
        messages.error(request, "Google 登入尚未設定，請先設定 GOOGLE_OAUTH_CLIENT_ID 與 GOOGLE_OAUTH_CLIENT_SECRET。")
        return redirect("login")

    state = secrets.token_urlsafe(32)
    request.session["social_google_state"] = state
    request.session["social_google_next"] = _safe_next_url(request.GET.get("next"))
    return redirect(build_google_authorize_url(request, state=state))


def social_google_callback(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = request.GET.get("error")
    if error:
        messages.error(request, f"Google 登入取消或失敗：{request.GET.get('error_description') or error}")
        return redirect("login")

    code = request.GET.get("code")
    state = request.GET.get("state")
    session_state = request.session.get("social_google_state")

    if not code or not state or not session_state or state != session_state:
        messages.error(request, "Google 登入驗證失敗，請重新操作。")
        return redirect("login")

    token_result = exchange_google_code(code, build_google_callback_uri(request))
    if not token_result.ok or not token_result.data or not token_result.data.get("access_token"):
        messages.error(request, "無法取得 Google 登入憑證，請確認 Google OAuth 設定。")
        return redirect("login")

    userinfo_result = fetch_google_userinfo(token_result.data["access_token"])
    if not userinfo_result.ok or not userinfo_result.data:
        messages.error(request, "無法取得 Google 帳號資料，請稍後再試。")
        return redirect("login")

    google_profile = userinfo_result.data
    google_sub = (google_profile.get("sub") or "").strip()
    email = (google_profile.get("email") or "").strip().lower()
    email_verified = google_profile.get("email_verified") in (True, "true", "True", "1", 1)
    display_name = (google_profile.get("name") or google_profile.get("given_name") or "").strip()

    if not google_sub or not email or not email_verified:
        messages.error(request, "Google 帳號未提供已驗證 Email，無法完成登入。")
        return redirect("login")

    with transaction.atomic():
        existing_profile = (
            MemberProfile.objects.select_for_update().select_related("user").filter(google_sub=google_sub).first()
        )
        if existing_profile:
            user = existing_profile.user
        else:
            user, created = _get_or_create_user_by_email(email, first_name=display_name)
            profile, _ = MemberProfile.objects.select_for_update().get_or_create(user=user)
            if profile.google_sub and profile.google_sub != google_sub:
                messages.error(request, "這個會員帳號已經綁定其他 Google 帳號。")
                return redirect("login")
            profile.google_sub = google_sub
            profile.google_email = email
            profile.google_bound_at = timezone.now()
            profile.save(update_fields=["google_sub", "google_email", "google_bound_at", "updated_at"])

    request.session.pop("social_google_state", None)
    next_url = request.session.pop("social_google_next", reverse("dashboard"))
    login(request, user)
    messages.success(request, "Google 登入成功。")
    return redirect(next_url)


def social_line_start(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if not line_social_login_configured():
        messages.error(request, "LINE 登入尚未設定，請先設定 LINE_LOGIN_CHANNEL_ID 與 LINE_LOGIN_CHANNEL_SECRET。")
        return redirect("login")

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    request.session["social_line_state"] = state
    request.session["social_line_nonce"] = nonce
    request.session["social_line_next"] = _safe_next_url(request.GET.get("next"))
    return redirect(build_line_social_authorize_url(request, state=state, nonce=nonce))


def social_line_callback(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    error = request.GET.get("error")
    if error:
        messages.error(request, f"LINE 登入取消或失敗：{request.GET.get('error_description') or error}")
        return redirect("login")

    code = request.GET.get("code")
    state = request.GET.get("state")
    session_state = request.session.get("social_line_state")

    if not code or not state or not session_state or state != session_state:
        messages.error(request, "LINE 登入驗證失敗，請重新操作。")
        return redirect("login")

    token_result = exchange_line_social_code(code, build_line_social_callback_uri(request))
    if not token_result.ok or not token_result.data or not token_result.data.get("access_token"):
        messages.error(request, "無法取得 LINE 登入憑證，請確認 LINE Login 設定與 callback URL。")
        return redirect("login")

    profile_result = fetch_line_social_profile(token_result.data["access_token"])
    if not profile_result.ok or not profile_result.data or not profile_result.data.get("userId"):
        messages.error(request, "無法取得 LINE 使用者資料，請稍後再試。")
        return redirect("login")

    line_profile = profile_result.data
    line_user_id = line_profile["userId"]

    with transaction.atomic():
        existing_profile = (
            MemberProfile.objects.select_for_update().select_related("user").filter(line_user_id=line_user_id).first()
        )
        if existing_profile:
            user = existing_profile.user
            request.session.pop("social_line_state", None)
            request.session.pop("social_line_nonce", None)
            next_url = request.session.pop("social_line_next", reverse("dashboard"))
            login(request, user)
            messages.success(request, "LINE 登入成功。")
            return redirect(next_url)

    request.session[PENDING_LINE_SESSION_KEY] = {
        "line_user_id": line_user_id,
        "line_display_name": line_profile.get("displayName", ""),
        "line_picture_url": line_profile.get("pictureUrl", ""),
        "next": request.session.get("social_line_next", reverse("dashboard")),
    }
    request.session.pop("social_line_state", None)
    request.session.pop("social_line_nonce", None)
    return redirect("social_line_complete_email")


def social_line_complete_email(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    pending = request.session.get(PENDING_LINE_SESSION_KEY)
    if not pending or not pending.get("line_user_id"):
        messages.info(request, "請先使用 LINE 登入。")
        return redirect("login")

    initial = {"first_name": pending.get("line_display_name", "")}
    if request.method == "POST":
        form = SocialEmailCompleteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data.get("first_name") or pending.get("line_display_name", "")
            phone = form.cleaned_data.get("phone", "")
            line_user_id = pending["line_user_id"]

            with transaction.atomic():
                existing_line_profile = (
                    MemberProfile.objects.select_for_update().select_related("user").filter(line_user_id=line_user_id).first()
                )
                if existing_line_profile:
                    user = existing_line_profile.user
                else:
                    user, created = _get_or_create_user_by_email(email, first_name=first_name, phone=phone)
                    profile, _ = MemberProfile.objects.select_for_update().get_or_create(user=user)
                    if profile.line_user_id and profile.line_user_id != line_user_id:
                        messages.error(request, "這個 Email 對應的會員已經綁定其他 LINE 帳號。")
                        return redirect("social_line_complete_email")
                    if not profile.phone and phone:
                        profile.phone = phone
                    profile.line_user_id = line_user_id
                    profile.line_display_name = pending.get("line_display_name", "")
                    profile.line_picture_url = pending.get("line_picture_url", "")
                    profile.line_bound_at = timezone.now()
                    profile.line_notify_enabled = True
                    profile.save(
                        update_fields=[
                            "phone",
                            "line_user_id",
                            "line_display_name",
                            "line_picture_url",
                            "line_bound_at",
                            "line_notify_enabled",
                            "updated_at",
                        ]
                    )

            next_url = _safe_next_url(pending.get("next"))
            request.session.pop(PENDING_LINE_SESSION_KEY, None)
            request.session.pop("social_line_next", None)
            login(request, user)
            messages.success(request, "LINE 登入設定完成，已登入會員中心。")
            return redirect(next_url)
    else:
        form = SocialEmailCompleteForm(initial=initial)

    return render(
        request,
        "pages/social_line_complete_email.html",
        {
            "form": form,
            "line_display_name": pending.get("line_display_name", ""),
        },
    )
