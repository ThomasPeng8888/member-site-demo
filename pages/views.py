from xml.sax.saxutils import escape

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


def home(request):
    return render(request, "pages/home.html")


def rewards(request):
    return render(request, "pages/rewards.html")


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
        "Disallow: /points/",
        "Disallow: /my-prizes/",
        "Disallow: /staff/",
        "Disallow: /lottery/spin/",
        "",
        f"Sitemap: {sitemap_url}",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    public_pages = [
        {"name": "home", "changefreq": "weekly", "priority": "1.0"},
        {"name": "activities", "changefreq": "weekly", "priority": "0.9"},
        {"name": "lottery", "changefreq": "weekly", "priority": "0.8"},
        {"name": "rewards", "changefreq": "weekly", "priority": "0.8"},
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

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {''.join(url_items)}
    </urlset>
    """

    return HttpResponse(xml, content_type="application/xml")
