from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from campaigns.models import Campaign


class Command(BaseCommand):
    help = "Create demo campaign draw data for 嘎比嘎比孔雀魚."

    def handle(self, *args, **options):
        now = timezone.now()

        campaign, created = Campaign.objects.update_or_create(
            slug="guppy-member-opening-draw",
            defaults={
                "campaign_name": "嘎比嘎比開站會員抽獎",
                "campaign_desc": "慶祝嘎比嘎比孔雀魚會員中心上線，會員完成登入後即可報名抽獎。",
                "image_emoji": "🐠",
                "prize_name": "嘎比嘎比神秘小禮包",
                "prize_desc": "包含孔雀魚飼料試用包與會員限定小禮。",
                "winner_count": 3,
                "alternate_count": 2,
                "register_start_at": now - timedelta(days=1),
                "register_end_at": now + timedelta(days=14),
                "draw_at": now + timedelta(days=15),
                "eligibility_rule": "限嘎比嘎比孔雀魚會員報名，每個會員限報名一次。",
                "redeem_expire_days": 30,
                "publish_flag": True,
                "status": "published",
                "notes": "Demo campaign created by seed_campaign_demo.",
            },
        )

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Demo campaign {action}: {campaign.campaign_name}"))
