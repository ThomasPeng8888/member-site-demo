from django.conf import settings


def social_contact_links(request):
    """Expose public social/contact URLs to all templates."""
    line_official_url = getattr(settings, "LINE_OFFICIAL_URL", "https://lin.ee/xyjkhCZ")
    facebook_page_url = getattr(
        settings,
        "FACEBOOK_PAGE_URL",
        "https://www.facebook.com/share/1DKhwBxNJT/?mibextid=wwXIfr",
    )
    facebook_messenger_url = (
        getattr(settings, "FACEBOOK_MESSENGER_URL", "")
        or getattr(settings, "FB_MESSENGER_URL", "")
        or facebook_page_url
    )

    return {
        "line_official_url_global": line_official_url,
        "facebook_page_url_global": facebook_page_url,
        "facebook_messenger_url_global": facebook_messenger_url,
        "facebook_messenger_direct_enabled": facebook_messenger_url != facebook_page_url,
    }
