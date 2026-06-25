from django.urls import path

from . import views

urlpatterns = [
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/<slug:slug>/", views.campaign_detail, name="campaign_detail"),
    path("campaigns/<slug:slug>/register/", views.register_campaign, name="register_campaign"),
    path("my-campaigns/", views.my_campaigns, name="my_campaigns"),
    path("my-campaigns/winners/<str:winner_id>/qr.png", views.campaign_winner_qr_png, name="campaign_winner_qr_png"),

    path("staff/campaigns/", views.staff_campaign_list, name="staff_campaign_list"),
    path("staff/campaigns/redeem/", views.staff_campaign_redeem, name="staff_campaign_redeem"),
    path("staff/campaigns/redeem/confirm/", views.redeem_campaign_coupon, name="redeem_campaign_coupon"),
    path("staff/campaigns/<slug:slug>/", views.staff_campaign_detail, name="staff_campaign_detail"),
    path("staff/campaigns/<slug:slug>/draw/", views.draw_campaign, name="draw_campaign"),
    path("staff/campaigns/winners/<str:winner_id>/void/", views.void_campaign_winner, name="void_campaign_winner"),
    path("staff/campaigns/winners/<str:winner_id>/promote/", views.promote_alternate, name="promote_alternate"),
]
