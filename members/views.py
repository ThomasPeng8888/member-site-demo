from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import MemberSignUpForm
from .models import MemberProfile


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

    activities = [
        {
            "icon": "🐧",
            "title": "企鵝餵食秀",
            "desc": "週六 14:30 ・ 會員優先入場",
        },
        {
            "icon": "🌙",
            "title": "夜宿水族館",
            "desc": "本月限定 ・ 會員專屬活動",
        },
        {
            "icon": "🐢",
            "title": "海龜保育講座",
            "desc": "報名即可獲得 100 點",
        },
    ]

    return render(
        request,
        "pages/dashboard.html",
        {
            "profile": profile,
            "display_name": display_name,
            "activities": activities,
        },
    )