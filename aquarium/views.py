from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from members.models import MemberProfile

from .models import (
    Activity,
    ActivityRegistration,
    MemberTicket,
    PointTransaction,
)


def activities(request):
    activity_list = Activity.objects.filter(is_published=True).order_by("starts_at")

    return render(
        request,
        "aquarium/activities.html",
        {
            "activities": activity_list,
        },
    )


def activity_detail(request, slug):
    activity = get_object_or_404(Activity, slug=slug, is_published=True)

    user_registration = None

    if request.user.is_authenticated:
        user_registration = ActivityRegistration.objects.filter(
            user=request.user,
            activity=activity,
            status="registered",
        ).first()

    return render(
        request,
        "aquarium/activity_detail.html",
        {
            "activity": activity,
            "user_registration": user_registration,
        },
    )


@login_required
@require_POST
def join_activity(request, slug):
    activity = get_object_or_404(Activity, slug=slug, is_published=True)

    if not activity.has_capacity:
        messages.error(request, "這個活動目前已額滿。")
        return redirect(activity.get_absolute_url())

    registration, created = ActivityRegistration.objects.get_or_create(
        user=request.user,
        activity=activity,
        defaults={"status": "registered"},
    )

    if not created and registration.status == "registered":
        messages.info(request, "你已經報名過這個活動了。")
        return redirect(activity.get_absolute_url())

    if not created and registration.status == "cancelled":
        registration.status = "registered"
        registration.save(update_fields=["status"])

    if activity.points_reward > 0:
        profile, _ = MemberProfile.objects.get_or_create(user=request.user)
        profile.points = F("points") + activity.points_reward
        profile.save(update_fields=["points"])
        profile.refresh_from_db()

        PointTransaction.objects.create(
            user=request.user,
            transaction_type="earn",
            points=activity.points_reward,
            title=f"報名活動：{activity.title}",
            note=f"活動報名獲得 {activity.points_reward} 點",
        )

    messages.success(request, "報名成功！活動資訊已加入你的會員紀錄。")
    return redirect(activity.get_absolute_url())


@login_required
def tickets(request):
    ticket_list = MemberTicket.objects.filter(user=request.user)

    return render(
        request,
        "aquarium/tickets.html",
        {
            "tickets": ticket_list,
        },
    )


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