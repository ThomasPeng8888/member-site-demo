from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("stores/", views.store_info, name="store_info"),
    path("rewards/", views.rewards, name="rewards"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
