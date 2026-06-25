from django.urls import path

from . import views

urlpatterns = [
    path("lottery/", views.lottery_page, name="lottery"),
    path("lottery/spin/", views.spin_lottery, name="spin_lottery"),
    path("my-prizes/", views.my_prizes, name="my_prizes"),
    path("my-prizes/<str:spin_code>/qr.png", views.regular_prize_qr_png, name="regular_prize_qr_png"),

    path("staff/redeem/", views.staff_redeem, name="staff_redeem"),
    path("staff/redeem/confirm/", views.redeem_regular_coupon, name="redeem_regular_coupon"),
]