from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from members.line_services import push_line_to_user
from members.models import MemberProfile
from members.permissions import can_access_staff_tools

from .models import (
    PointTransaction,
    StaffPointGrant,
)

POINT_AMOUNT_UNIT = 300


def activities(request):
    messages.info(request, "活動報名功能目前暫停使用，請改由活動抽獎查看目前可參加的活動。")
    return redirect("campaign_list")


def activity_detail(request, slug):
    messages.info(request, "活動報名功能目前暫停使用，請改由活動抽獎查看目前可參加的活動。")
    return redirect("campaign_list")


@login_required
@require_POST
def join_activity(request, slug):
    messages.info(request, "活動報名功能目前暫停使用，請改由活動抽獎查看目前可參加的活動。")
    return redirect("campaign_list")

@login_required
def tickets(request):
    messages.info(request, "票券功能目前暫停使用，請改由會員抽獎或活動抽獎查看相關獎品資訊。")
    return redirect("dashboard")


@login_required
def points(request):
    transaction_list = PointTransaction.objects.filter(user=request.user)

    return render(
        request,
        "aquarium/points.html",
        {
            "transactions": transaction_list,
        },
    )


def staff_required(user):
    return can_access_staff_tools(user)


def find_member_by_keyword(keyword):
    User = get_user_model()
    keyword = keyword.strip()

    if not keyword:
        return None

    profile_match = MemberProfile.objects.filter(
        Q(member_no__iexact=keyword)
        | Q(phone__iexact=keyword)
        | Q(user__email__iexact=keyword)
        | Q(user__username__iexact=keyword)
    ).select_related("user").first()

    if profile_match:
        return profile_match.user

    return User.objects.filter(
        Q(email__iexact=keyword)
        | Q(username__iexact=keyword)
    ).first()


@user_passes_test(staff_required, login_url="login")
def staff_add_points(request):
    target_user = None
    target_profile = None

    if request.method == "POST":
        keyword = request.POST.get("keyword", "").strip()
        purchase_amount_raw = request.POST.get("purchase_amount", "").strip()
        note = request.POST.get("note", "").strip()

        target_user = find_member_by_keyword(keyword)

        if not target_user:
            messages.error(request, "找不到會員，請確認會員編號、Email 或完整手機是否正確。")
            return redirect("staff_add_points")

        try:
            purchase_amount = int(purchase_amount_raw)
        except ValueError:
            messages.error(request, "消費金額請輸入整數。")
            return redirect("staff_add_points")

        if purchase_amount <= 0:
            messages.error(request, "消費金額必須大於 0。")
            return redirect("staff_add_points")

        earned_points = purchase_amount // POINT_AMOUNT_UNIT

        if earned_points <= 0:
            messages.error(
                request,
                f"本次消費 {purchase_amount} 元，未滿 {POINT_AMOUNT_UNIT} 元，沒有可累積點數。",
            )
            return redirect("staff_add_points")

        with transaction.atomic():
            target_profile, _ = (
                MemberProfile.objects
                .select_for_update()
                .get_or_create(user=target_user)
            )

            target_profile.points += earned_points
            target_profile.save(update_fields=["points", "updated_at"])

            StaffPointGrant.objects.create(
                member=target_user,
                staff=request.user,
                purchase_amount=purchase_amount,
                earned_points=earned_points,
                note=note,
            )

            PointTransaction.objects.create(
                user=target_user,
                transaction_type="earn",
                points=earned_points,
                title=f"消費集點：{purchase_amount} 元",
                note=(
                    f"每 {POINT_AMOUNT_UNIT} 元累積 1 點，本次獲得 {earned_points} 點。"
                    f"{' 備註：' + note if note else ''}"
                ),
            )

        push_line_to_user(
            target_user,
            (
                "嘎比嘎比孔雀魚消費集點通知 🐠\n"
                f"本次消費：{purchase_amount} 元\n"
                f"獲得點數：{earned_points} 點\n"
                f"目前點數：{target_profile.points} 點"
            ),
        )

        messages.success(
            request,
            f"加點成功！會員 {target_user.email or target_user.username} "
            f"本次獲得 {earned_points} 點，目前共有 {target_profile.points} 點。",
        )
        return redirect("staff_add_points")

    keyword = request.GET.get("keyword", "").strip()

    if keyword:
        target_user = find_member_by_keyword(keyword)

        if target_user:
            target_profile, _ = MemberProfile.objects.get_or_create(user=target_user)
        else:
            messages.error(request, "找不到會員，請確認會員編號、Email 或完整手機是否正確。")

    recent_grants = StaffPointGrant.objects.select_related(
        "member",
        "staff",
    )[:10]

    return render(
        request,
        "aquarium/staff_add_points.html",
        {
            "point_amount_unit": POINT_AMOUNT_UNIT,
            "target_user": target_user,
            "target_profile": target_profile,
            "recent_grants": recent_grants,
        },
    )
