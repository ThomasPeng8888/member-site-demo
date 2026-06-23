from django.shortcuts import render


def home(request):
    return render(request, "pages/home.html")


def login_page(request):
    return render(request, "pages/login.html")


def register_page(request):
    return render(request, "pages/register.html")


def dashboard(request):
    return render(request, "pages/dashboard.html")


def rewards(request):
    return render(request, "pages/rewards.html")