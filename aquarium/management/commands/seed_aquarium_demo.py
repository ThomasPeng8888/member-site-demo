from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from aquarium.models import Activity


class Command(BaseCommand):
    help = "Create demo aquarium activities."

    def handle(self, *args, **options):
        now = timezone.now()

        demo_activities = [
            {
                "title": "企鵝餵食秀",
                "slug": "penguin-feeding-show",
                "category": "show",
                "summary": "近距離觀看企鵝餵食時刻，了解牠們的生活習性。",
                "description": "這是一場適合親子一起參加的輕鬆活動。飼育員會介紹企鵝的飲食、生活環境與保育知識，會員報名後可以優先入場。",
                "image_emoji": "🐧",
                "starts_at": now + timedelta(days=3, hours=2),
                "location": "極地企鵝區",
                "points_reward": 50,
                "max_capacity": 30,
            },
            {
                "title": "夜宿水族館",
                "slug": "sleepover-aquarium",
                "category": "event",
                "summary": "在夜晚的水族館裡，感受完全不同的海洋氛圍。",
                "description": "夜宿水族館是會員限定活動，包含夜間導覽、海洋故事時間與隔日早餐。適合親子、朋友與喜歡海洋的旅客。",
                "image_emoji": "🌙",
                "starts_at": now + timedelta(days=10, hours=6),
                "location": "海洋隧道",
                "points_reward": 120,
                "max_capacity": 20,
            },
            {
                "title": "海龜保育講座",
                "slug": "sea-turtle-conservation",
                "category": "conservation",
                "summary": "了解海龜保育、海洋塑膠污染與日常減塑行動。",
                "description": "由保育團隊分享海龜救援與野放故事，帶會員認識海洋環境議題。活動結束後可獲得會員點數。",
                "image_emoji": "🐢",
                "starts_at": now + timedelta(days=7, hours=1),
                "location": "教育教室 A",
                "points_reward": 80,
                "max_capacity": 40,
            },
        ]

        for data in demo_activities:
            Activity.objects.update_or_create(
                slug=data["slug"],
                defaults=data,
            )

        self.stdout.write(self.style.SUCCESS("Demo aquarium activities created."))