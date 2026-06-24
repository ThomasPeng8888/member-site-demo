from django.urls import path

from . import views

urlpatterns = [
    path("lottery/", views.lottery_page, name="lottery"),
    path("lottery/spin/", views.spin_lottery, name="spin_lottery"),
    path("my-prizes/", views.my_prizes, name="my_prizes"),
]