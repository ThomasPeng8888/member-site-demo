import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from aquarium.models import PointTransaction
from members.models import MemberProfile

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