from xml.sax.saxutils import escape

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import NewsPost, Product, StoreInfo


def published_news_queryset():
    return NewsPost.objects.filter(is_published=True, published_at__lte=timezone.now())


def visible_products_queryset():
    return Product.objects.filter(is_published=True).exclude(status="hidden")


def visible_stores_queryset():
    return StoreInfo.objects.filter(is_published=True)


def home(request):
    latest_news = published_news_queryset()[:3]
    featured_products = visible_products_queryset().filter(is_featured=True)[:3]

    if not featured_products.exists():
        featured_products = visible_products_queryset()[:3]

    carousel_products = list(
        visible_products_queryset()
        .filter(image__isnull=False)
        .exclude(image="")
        .order_by("-is_featured", "sort_order", "-created_at", "-id")[:5]
    )

    stores = visible_stores_queryset()[:2]

    return render(
        request,
        "pages/home.html",
        {
            "latest_news": latest_news,
            "featured_products": featured_products,
            "carousel_products": carousel_products,
            "stores": stores,
        },
    )


def rewards(request):
    messages.info(request, "此會員服務目前暫停使用，請改由會員抽獎或活動抽獎查看相關獎品資訊。")
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("home")


def news_list(request):
    posts = published_news_queryset()
    return render(request, "pages/news_list.html", {"posts": posts})


def news_detail(request, slug):
    post = get_object_or_404(published_news_queryset(), slug=slug)
    return render(request, "pages/news_detail.html", {"post": post})


def product_list(request):
    products = visible_products_queryset()
    return render(request, "pages/product_list.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(visible_products_queryset(), slug=slug)
    return render(request, "pages/product_detail.html", {"product": product})


def store_info(request):
    stores = visible_stores_queryset()
    return render(request, "pages/store_info.html", {"stores": stores})


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap_xml"))

    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /register/",
        "Disallow: /tickets/",
        "Disallow: /rewards/",
        "Disallow: /points/",
        "Disallow: /my-prizes/",
        "Disallow: /my-campaigns/",
        "Disallow: /line/",
        "Disallow: /member/qr.png",
        "Disallow: /staff/",
        "Disallow: /lottery/spin/",
        "",
        f"Sitemap: {sitemap_url}",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    public_pages = [
        {"name": "home", "changefreq": "weekly", "priority": "1.0"},
        {"name": "news_list", "changefreq": "weekly", "priority": "0.9"},
        {"name": "product_list", "changefreq": "weekly", "priority": "0.9"},
        {"name": "store_info", "changefreq": "monthly", "priority": "0.8"},
        {"name": "activities", "changefreq": "weekly", "priority": "0.8"},
        {"name": "campaign_list", "changefreq": "weekly", "priority": "0.8"},
    ]

    url_items = []

    for page in public_pages:
        location = request.build_absolute_uri(reverse(page["name"]))
        url_items.append(
            f"""
            <url>
                <loc>{escape(location)}</loc>
                <changefreq>{page["changefreq"]}</changefreq>
                <priority>{page["priority"]}</priority>
            </url>
            """
        )

    try:
        for post in published_news_queryset().only("slug"):
            location = request.build_absolute_uri(post.get_absolute_url())
            url_items.append(
                f"""
                <url>
                    <loc>{escape(location)}</loc>
                    <changefreq>weekly</changefreq>
                    <priority>0.7</priority>
                </url>
                """
            )
    except Exception:
        pass

    try:
        for product in visible_products_queryset().only("slug"):
            location = request.build_absolute_uri(product.get_absolute_url())
            url_items.append(
                f"""
                <url>
                    <loc>{escape(location)}</loc>
                    <changefreq>weekly</changefreq>
                    <priority>0.7</priority>
                </url>
                """
            )
    except Exception:
        pass

    try:
        from aquarium.models import Activity

        for activity in Activity.objects.filter(is_published=True).only("slug"):
            location = request.build_absolute_uri(activity.get_absolute_url())
            url_items.append(
                f"""
                <url>
                    <loc>{escape(location)}</loc>
                    <changefreq>weekly</changefreq>
                    <priority>0.7</priority>
                </url>
                """
            )
    except Exception:
        # Keep sitemap available even during first deployment before migrations.
        pass

    try:
        from campaigns.models import Campaign

        for campaign in Campaign.objects.filter(
            publish_flag=True,
            status__in=["published", "closed", "drawn"],
        ).only("slug"):
            location = request.build_absolute_uri(campaign.get_absolute_url())
            url_items.append(
                f"""
                <url>
                    <loc>{escape(location)}</loc>
                    <changefreq>weekly</changefreq>
                    <priority>0.7</priority>
                </url>
                """
            )
    except Exception:
        # Keep sitemap available even during first deployment before migrations.
        pass

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {''.join(url_items)}
    </urlset>
    """

    return HttpResponse(xml, content_type="application/xml")
