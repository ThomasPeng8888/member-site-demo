import secrets
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from aquarium.models import PointTransaction
from members.line_services import push_line_to_user
from members.models import MemberProfile
from members.permissions import can_access_staff_tools

from .models import LOTTERY_COST_POINTS, LotteryPrize, LotterySpin


def choose_weighted_prize(prizes):
    total_weight = sum(int(prize.weight or 0) for prize in prizes)

    if total_weight <= 0:
        return None

    ticket = secrets.randbelow(total_weight) + 1
    cursor = 0

    for prize in prizes:
        cursor += int(prize.weight or 0)
        if ticket <= cursor:
            return prize

    return prizes[-1]


def available_prize_queryset():
    now = timezone.now()

    return (
        LotteryPrize.objects
        .filter(enabled=True)
        .filter(Q(stock__isnull=True) | Q(stock__gt=0))
        .filter(Q(start_at__isnull=True) | Q(start_at__lte=now))
        .filter(Q(end_at__isnull=True) | Q(end_at__gte=now))
        .order_by("sort_order", "id")
    )


def lottery_page(request):
    prizes = available_prize_queryset()

    profile = None
    recent_spins = []

    if request.user.is_authenticated:
        profile, _ = MemberProfile.objects.get_or_create(user=request.user)
        recent_spins = LotterySpin.objects.filter(user=request.user)[:5]

    return render(
        request,
        "lottery/lottery.html",
        {
            "prizes": prizes,
            "profile": profile,
            "recent_spins": recent_spins,
            "lottery_cost": LOTTERY_COST_POINTS,
        },
    )


@login_required
@require_POST
def spin_lottery(request):
    with transaction.atomic():
        profile, _ = (
            MemberProfile.objects
            .select_for_update()
            .get_or_create(user=request.user)
        )

        if profile.points < LOTTERY_COST_POINTS:
            messages.error(
                request,
                f"點數不足，目前有 {profile.points} 點，抽獎需要 {LOTTERY_COST_POINTS} 點。",
            )
            return redirect("lottery")

        prizes = list(available_prize_queryset().select_for_update())

        if not prizes:
            messages.error(request, "目前沒有可抽的獎項，請稍後再試。")
            return redirect("lottery")

        prize = choose_weighted_prize(prizes)

        if not prize:
            messages.error(request, "獎項權重設定有誤，請聯絡管理員。")
            return redirect("lottery")

        stock_before = prize.stock
        stock_after = prize.stock

        if prize.stock is not None:
            if prize.stock <= 0:
                messages.error(request, "獎項庫存不足，請稍後再試。")
                return redirect("lottery")

            prize.stock = prize.stock - 1
            stock_after = prize.stock
            prize.save(update_fields=["stock", "updated_at"])

        profile.points = profile.points - LOTTERY_COST_POINTS
        profile.save(update_fields=["points", "updated_at"])

        spin = LotterySpin.objects.create(
            user=request.user,
            cost_points=LOTTERY_COST_POINTS,
            prize=prize,
            prize_name=prize.prize_name,
            stock_before=stock_before,
            stock_after=stock_after,
            balance_after=profile.points,
            expire_at=timezone.now() + timedelta(days=90),
        )

        redeem_url = request.build_absolute_uri(
            reverse("my_prizes")
        )

        spin.redeem_qr_payload = (
            f"{redeem_url}?code={spin.redeem_code}&spin={spin.spin_code}"
        )
        spin.save(update_fields=["redeem_qr_payload"])

        PointTransaction.objects.create(
            user=request.user,
            transaction_type="spend",
            points=LOTTERY_COST_POINTS,
            title=f"常態抽獎：{prize.prize_name}",
            note=f"抽獎編號：{spin.spin_code}，兌換碼：{spin.redeem_code}",
        )

    push_line_to_user(
        request.user,
        (
            "嘎比嘎比孔雀魚抽獎結果 🎁\n"
            f"恭喜抽中：{prize.prize_name}\n"
            f"兌換碼：{spin.redeem_code}\n"
            f"到期時間：{spin.expire_at:%Y/%m/%d %H:%M}\n"
            f"目前點數：{spin.balance_after} 點"
        ),
    )

    messages.success(
        request,
        f"恭喜抽中「{prize.prize_name}」！兌換碼已產生，可到我的獎品查看。",
    )
    return redirect("my_prizes")


@login_required
def my_prizes(request):
    spins = LotterySpin.objects.filter(user=request.user)

    return render(
        request,
        "lottery/my_prizes.html",
        {
            "spins": spins,
        },
    )

def staff_required(user):
    return can_access_staff_tools(user)


@user_passes_test(staff_required, login_url="login")
def staff_redeem(request):
    code = request.GET.get("code", "").strip()
    target_spin = None

    if code:
        target_spin = LotterySpin.objects.filter(
            redeem_code__iexact=code
        ).select_related("user", "prize").first()

        if target_spin and target_spin.is_expired and target_spin.coupon_status == "unredeemed":
            target_spin.coupon_status = "expired"
            target_spin.save(update_fields=["coupon_status"])

    return render(
        request,
        "lottery/staff_redeem.html",
        {
            "code": code,
            "target_spin": target_spin,
        },
    )


@user_passes_test(staff_required, login_url="login")
@require_POST
def redeem_regular_coupon(request):
    redeem_code = request.POST.get("redeem_code", "").strip()

    if not redeem_code:
        messages.error(request, "請輸入兌換碼。")
        return redirect("staff_redeem")

    with transaction.atomic():
        spin = (
            LotterySpin.objects
            .select_for_update()
            .select_related("user", "prize")
            .filter(redeem_code__iexact=redeem_code)
            .first()
        )

        if not spin:
            messages.error(request, "找不到這張兌換券。")
            return redirect("staff_redeem")

        if spin.coupon_status == "redeemed":
            messages.error(request, "這張兌換券已經核銷過了。")
            return redirect(f"{reverse('staff_redeem')}?code={spin.redeem_code}")

        if spin.coupon_status == "void":
            messages.error(request, "這張兌換券已作廢，無法核銷。")
            return redirect(f"{reverse('staff_redeem')}?code={spin.redeem_code}")

        if spin.is_expired:
            spin.coupon_status = "expired"
            spin.save(update_fields=["coupon_status"])
            messages.error(request, "這張兌換券已過期，無法核銷。")
            return redirect(f"{reverse('staff_redeem')}?code={spin.redeem_code}")

        spin.coupon_status = "redeemed"
        spin.redeemed_at = timezone.now()
        spin.redeemed_by = request.user.username or request.user.email
        spin.save(
            update_fields=[
                "coupon_status",
                "redeemed_at",
                "redeemed_by",
            ]
        )

    push_line_to_user(
        spin.user,
        (
            "嘎比嘎比孔雀魚獎品核銷通知 ✅\n"
            f"獎品：{spin.prize_name}\n"
            f"兌換碼：{spin.redeem_code}\n"
            f"核銷時間：{spin.redeemed_at:%Y/%m/%d %H:%M}"
        ),
    )

    messages.success(request, f"核銷成功：{spin.prize_name}")
    return redirect(f"{reverse('staff_redeem')}?code={spin.redeem_code}")