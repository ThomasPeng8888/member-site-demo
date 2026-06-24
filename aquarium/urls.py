from django.urls import path

from . import views

urlpatterns = [
    path("activities/", views.activities, name="activities"),
    path("activities/<slug:slug>/", views.activity_detail, name="activity_detail"),
    path("activities/<slug:slug>/join/", views.join_activity, name="join_activity"),
    path("tickets/", views.tickets, name="tickets"),
    path("points/", views.points, name="points"),
    path("staff/add-points/", views.staff_add_points, name="staff_add_points"),
]