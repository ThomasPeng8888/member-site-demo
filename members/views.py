from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from aquarium.models import Activity, PointTransaction
from .forms import MemberSignUpForm
from .models import MemberProfile
from .qr_utils import qr_png_response


def register_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = MemberSignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = MemberSignUpForm()

    return render(request, "pages/register.html", {"form": form})


@login_required
def dashboard(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)

    display_name = (
        request.user.first_name
        or request.user.email
        or request.user.username
    )

    upcoming_activities = Activity.objects.filter(
        is_published=True,
        starts_at__gte=timezone.now(),
    ).order_by("starts_at")[:3]

    recent_transactions = PointTransaction.objects.filter(
        user=request.user,
    ).order_by("-created_at")[:5]

    registered_activity_count = request.user.activity_registrations.filter(
        status="registered",
    ).count()

    return render(
        request,
        "pages/dashboard.html",
        {
            "profile": profile,
            "display_name": display_name,
            "upcoming_activities": upcoming_activities,
            "recent_transactions": recent_transactions,
            "registered_activity_count": registered_activity_count,
        },
    )

@login_required
def member_qr_png(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    staff_add_points_url = request.build_absolute_uri(
        f"{reverse('staff_add_points')}?{urlencode({'keyword': profile.member_no})}"
    )
    return qr_png_response(
        staff_add_points_url,
        filename=f"guppyguppy-member-{profile.member_no}.png",
    )
