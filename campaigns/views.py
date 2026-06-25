import random
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from members.line_services import push_line_to_user
from members.permissions import can_access_staff_tools, can_manage_campaigns
from members.qr_utils import qr_png_response

from .models import Campaign, CampaignRegistration, CampaignWinner


CAMPAIGN_VOID_STATUSES = ["void", "expired"]


def published_campaign_queryset():
    return Campaign.objects.filter(
        publish_flag=True,
        status__in=["published", "closed", "drawn"],
    ).order_by("-register_start_at", "-id")


def campaign_staff_required(user):
    return can_access_staff_tools(user)


def campaign_manager_required(user):
    return can_manage_campaigns(user)


def build_campaign_redeem_payload(request, winner):
    redeem_url = request.build_absolute_uri(reverse("staff_campaign_redeem"))
    return f"{redeem_url}?code={winner.redeem_code}"


def mark_winner_expired_if_needed(winner):
    if winner and winner.is_expired and winner.winner_status == "unredeemed":
        winner.winner_status = "expired"
        winner.save(update_fields=["winner_status"])


def active_primary_count(campaign):
    return (
        campaign.winners
        .filter(winner_type="primary")
        .exclude(winner_status__in=CAMPAIGN_VOID_STATUSES)
        .count()
    )


def campaign_list(request):
    campaigns = published_campaign_queryset()

    return render(
        request,
        "campaigns/campaign_list.html",
        {
            "campaigns": campaigns,
        },
    )


def campaign_detail(request, slug):
    campaign = get_object_or_404(published_campaign_queryset(), slug=slug)
    registration = None
    winner = None

    if request.user.is_authenticated:
        registration = CampaignRegistration.objects.filter(
            campaign=campaign,
            user=request.user,
        ).first()
        winner = CampaignWinner.objects.filter(
            campaign=campaign,
            user=request.user,
        ).first()
        mark_winner_expired_if_needed(winner)

    return render(
        request,
        "campaigns/campaign_detail.html",
        {
            "campaign": campaign,
            "registration": registration,
            "winner": winner,
            "now": timezone.now(),
        },
    )


@login_required
@require_POST
def register_campaign(request, slug):
    campaign = get_object_or_404(published_campaign_queryset(), slug=slug)

    if not campaign.registration_is_open:
        messages.error(request, "目前不是這個活動抽獎的報名時間。")
        return redirect(campaign.get_absolute_url())

    with transaction.atomic():
        registration, created = CampaignRegistration.objects.select_for_update().get_or_create(
            campaign=campaign,
            user=request.user,
            defaults={"status": "registered"},
        )

        if created:
            push_line_to_user(
                request.user,
                (
                    "嘎比嘎比孔雀魚活動抽獎報名成功 🐠\n"
                    f"活動：{campaign.campaign_name}\n"
                    "抽獎結果公布後，可在會員中心或 LINE 查詢。"
                ),
            )
            messages.success(request, "報名成功！抽獎結果公布後可以在我的活動抽獎查看。")
            return redirect(campaign.get_absolute_url())

        if registration.status == "registered":
            messages.info(request, "你已經報名過這個活動抽獎了。")
            return redirect(campaign.get_absolute_url())

        registration.status = "registered"
        registration.register_time = timezone.now()
        registration.save(update_fields=["status", "register_time"])

    push_line_to_user(
        request.user,
        (
            "嘎比嘎比孔雀魚活動抽獎已重新報名 🐠\n"
            f"活動：{campaign.campaign_name}"
        ),
    )
    messages.success(request, "已重新報名這個活動抽獎。")
    return redirect(campaign.get_absolute_url())


@login_required
def my_campaigns(request):
    registrations = CampaignRegistration.objects.filter(user=request.user).select_related("campaign")
    winners = CampaignWinner.objects.filter(user=request.user).select_related("campaign")

    for winner in winners:
        mark_winner_expired_if_needed(winner)

    return render(
        request,
        "campaigns/my_campaigns.html",
        {
            "registrations": registrations,
            "winners": winners,
        },
    )


@login_required
def campaign_winner_qr_png(request, winner_id):
    queryset = CampaignWinner.objects.filter(winner_id=winner_id)

    if not (can_access_staff_tools(request.user) or can_manage_campaigns(request.user)):
        queryset = queryset.filter(user=request.user)

    winner = get_object_or_404(queryset)
    staff_redeem_url = request.build_absolute_uri(
        f"{reverse('staff_campaign_redeem')}?{urlencode({'code': winner.redeem_code})}"
    )

    return qr_png_response(
        staff_redeem_url,
        filename=f"gabi-campaign-{winner.redeem_code}.png",
    )


@user_passes_test(campaign_manager_required, login_url="login")
def staff_campaign_list(request):
    campaigns = Campaign.objects.all().order_by("-register_start_at", "-id")

    return render(
        request,
        "campaigns/staff_campaign_list.html",
        {
            "campaigns": campaigns,
        },
    )


@user_passes_test(campaign_manager_required, login_url="login")
def staff_campaign_detail(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    registrations = (
        CampaignRegistration.objects
        .filter(campaign=campaign)
        .select_related("user")
        .order_by("status", "register_time")[:200]
    )
    winners = (
        CampaignWinner.objects
        .filter(campaign=campaign)
        .select_related("user")
        .order_by("winner_type", "winner_rank")
    )

    for winner in winners:
        mark_winner_expired_if_needed(winner)

    return render(
        request,
        "campaigns/staff_campaign_detail.html",
        {
            "campaign": campaign,
            "registrations": registrations,
            "winners": winners,
            "active_primary_count": active_primary_count(campaign),
        },
    )


@user_passes_test(campaign_manager_required, login_url="login")
@require_POST
def draw_campaign(request, slug):
    created_winners = []

    with transaction.atomic():
        campaign = Campaign.objects.select_for_update().get(slug=slug)

        if campaign.winners.select_for_update().exists():
            messages.error(request, "這個活動已經抽過獎，不能重複抽獎。")
            return redirect("staff_campaign_detail", slug=campaign.slug)

        registrations = list(
            CampaignRegistration.objects
            .select_for_update()
            .filter(campaign=campaign, status="registered")
            .select_related("user")
        )

        if not registrations:
            messages.error(request, "目前沒有已報名會員，無法抽獎。")
            return redirect("staff_campaign_detail", slug=campaign.slug)

        random.SystemRandom().shuffle(registrations)

        primary_slots = min(campaign.winner_count, len(registrations))
        remaining_after_primary = max(len(registrations) - primary_slots, 0)
        alternate_slots = min(campaign.alternate_count, remaining_after_primary)
        total_slots = primary_slots + alternate_slots

        draw_time = timezone.now()
        expire_at = draw_time + timedelta(days=campaign.redeem_expire_days or 30)
        selected_registrations = registrations[:total_slots]

        primary_created = 0
        alternate_created = 0

        for index, registration in enumerate(selected_registrations):
            if index < primary_slots:
                winner_type = "primary"
                winner_rank = index + 1
                primary_created += 1
            else:
                winner_type = "alternate"
                winner_rank = index - primary_slots + 1
                alternate_created += 1

            winner = CampaignWinner.objects.create(
                campaign=campaign,
                user=registration.user,
                campaign_name=campaign.campaign_name,
                prize_name=campaign.prize_name,
                prize_desc=campaign.prize_desc,
                winner_type=winner_type,
                winner_rank=winner_rank,
                winner_status="unredeemed",
                draw_time=draw_time,
                expire_at=expire_at,
            )
            winner.redeem_qr_payload = build_campaign_redeem_payload(request, winner)
            winner.save(update_fields=["redeem_qr_payload"])
            created_winners.append(winner)

        campaign.status = "drawn"
        campaign.draw_executed_at = draw_time
        campaign.save(update_fields=["status", "draw_executed_at", "updated_at"])

    for winner in created_winners:
        if winner.winner_type == "primary":
            line_text = (
                "嘎比嘎比孔雀魚活動抽獎中獎通知 🎉\n"
                f"活動：{winner.campaign_name}\n"
                f"獎品：{winner.prize_name}\n"
                f"兌換碼：{winner.redeem_code}\n"
                f"到期時間：{winner.expire_at:%Y/%m/%d %H:%M}"
            )
        else:
            line_text = (
                "嘎比嘎比孔雀魚活動抽獎候補通知 🐠\n"
                f"活動：{winner.campaign_name}\n"
                f"獎品：{winner.prize_name}\n"
                "目前為候補資格，遞補成正取後會再通知你。"
            )
        push_line_to_user(winner.user, line_text)

    messages.success(
        request,
        f"抽獎完成：正取 {primary_created} 位，候補 {alternate_created} 位。",
    )
    return redirect("staff_campaign_detail", slug=campaign.slug)


@user_passes_test(campaign_manager_required, login_url="login")
@require_POST
def void_campaign_winner(request, winner_id):
    with transaction.atomic():
        winner = (
            CampaignWinner.objects
            .select_for_update()
            .select_related("campaign")
            .get(winner_id=winner_id)
        )

        if winner.winner_status == "redeemed":
            messages.error(request, "已核銷的活動獎品不能作廢。")
            return redirect("staff_campaign_detail", slug=winner.campaign.slug)

        winner.winner_status = "void"
        winner.save(update_fields=["winner_status"])

    messages.success(request, f"已作廢 {winner.user} 的活動兌換資格。")
    return redirect("staff_campaign_detail", slug=winner.campaign.slug)


@user_passes_test(campaign_manager_required, login_url="login")
@require_POST
def promote_alternate(request, winner_id):
    with transaction.atomic():
        winner = (
            CampaignWinner.objects
            .select_for_update()
            .select_related("campaign", "user")
            .get(winner_id=winner_id)
        )
        campaign = Campaign.objects.select_for_update().get(pk=winner.campaign_id)

        if winner.winner_type != "alternate":
            messages.error(request, "只有候補名單可以遞補成正取。")
            return redirect("staff_campaign_detail", slug=campaign.slug)

        if winner.winner_status != "unredeemed":
            messages.error(request, "這位候補目前狀態不能遞補。")
            return redirect("staff_campaign_detail", slug=campaign.slug)

        if winner.is_expired:
            winner.winner_status = "expired"
            winner.save(update_fields=["winner_status"])
            messages.error(request, "這位候補兌換資格已過期，不能遞補。")
            return redirect("staff_campaign_detail", slug=campaign.slug)

        current_active_primary_count = active_primary_count(campaign)
        if current_active_primary_count >= campaign.winner_count:
            messages.error(request, "目前正取名額尚未空出。請先作廢或標記過期一位正取，再進行候補遞補。")
            return redirect("staff_campaign_detail", slug=campaign.slug)

        next_primary_rank = (
            campaign.winners
            .filter(winner_type="primary")
            .aggregate(max_rank=Max("winner_rank"))
            .get("max_rank")
            or 0
        ) + 1

        now = timezone.now()
        winner.winner_type = "primary"
        winner.winner_rank = next_primary_rank
        winner.promoted_at = now
        winner.expire_at = now + timedelta(days=campaign.redeem_expire_days or 30)
        winner.redeem_qr_payload = build_campaign_redeem_payload(request, winner)
        winner.save(
            update_fields=[
                "winner_type",
                "winner_rank",
                "promoted_at",
                "expire_at",
                "redeem_qr_payload",
            ]
        )

    push_line_to_user(
        winner.user,
        (
            "嘎比嘎比孔雀魚活動抽獎遞補通知 🎉\n"
            f"活動：{winner.campaign_name}\n"
            f"你已遞補為正取。\n"
            f"獎品：{winner.prize_name}\n"
            f"兌換碼：{winner.redeem_code}\n"
            f"到期時間：{winner.expire_at:%Y/%m/%d %H:%M}"
        ),
    )

    messages.success(request, f"已將候補 {winner.user} 遞補為正取。")
    return redirect("staff_campaign_detail", slug=campaign.slug)


@user_passes_test(campaign_staff_required, login_url="login")
def staff_campaign_redeem(request):
    code = request.GET.get("code", "").strip()
    target_winner = None

    if code:
        target_winner = (
            CampaignWinner.objects
            .filter(redeem_code__iexact=code)
            .select_related("campaign", "user")
            .first()
        )
        mark_winner_expired_if_needed(target_winner)

    return render(
        request,
        "campaigns/staff_campaign_redeem.html",
        {
            "code": code,
            "target_winner": target_winner,
        },
    )


@user_passes_test(campaign_staff_required, login_url="login")
@require_POST
def redeem_campaign_coupon(request):
    redeem_code = request.POST.get("redeem_code", "").strip()

    if not redeem_code:
        messages.error(request, "請輸入活動兌換碼。")
        return redirect("staff_campaign_redeem")

    with transaction.atomic():
        winner = (
            CampaignWinner.objects
            .select_for_update()
            .select_related("campaign", "user")
            .filter(redeem_code__iexact=redeem_code)
            .first()
        )

        if not winner:
            messages.error(request, "找不到這張活動兌換券。")
            return redirect("staff_campaign_redeem")

        if winner.winner_type != "primary":
            messages.error(request, "候補名單尚未遞補為正取，不能核銷。")
            return redirect(f"{reverse('staff_campaign_redeem')}?code={winner.redeem_code}")

        if winner.winner_status == "redeemed":
            messages.error(request, "這張活動兌換券已經核銷過了。")
            return redirect(f"{reverse('staff_campaign_redeem')}?code={winner.redeem_code}")

        if winner.winner_status == "void":
            messages.error(request, "這張活動兌換券已作廢，無法核銷。")
            return redirect(f"{reverse('staff_campaign_redeem')}?code={winner.redeem_code}")

        if winner.is_expired or winner.winner_status == "expired":
            winner.winner_status = "expired"
            winner.save(update_fields=["winner_status"])
            messages.error(request, "這張活動兌換券已過期，無法核銷。")
            return redirect(f"{reverse('staff_campaign_redeem')}?code={winner.redeem_code}")

        winner.winner_status = "redeemed"
        winner.redeemed_at = timezone.now()
        winner.redeemed_by = request.user.get_username()
        winner.save(update_fields=["winner_status", "redeemed_at", "redeemed_by"])

    push_line_to_user(
        winner.user,
        (
            "嘎比嘎比孔雀魚活動獎品核銷通知 ✅\n"
            f"活動：{winner.campaign_name}\n"
            f"獎品：{winner.prize_name}\n"
            f"兌換碼：{winner.redeem_code}\n"
            f"核銷時間：{winner.redeemed_at:%Y/%m/%d %H:%M}"
        ),
    )

    messages.success(request, f"活動獎品核銷成功：{winner.prize_name}")
    return redirect(f"{reverse('staff_campaign_redeem')}?code={winner.redeem_code}")
