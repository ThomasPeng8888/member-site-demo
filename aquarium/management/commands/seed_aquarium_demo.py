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
                "title": "孔雀魚入門交流",
                "slug": "penguin-feeding-show",
                "category": "show",
                "summary": "認識孔雀魚品系、基本飼育環境與新手常見問題。",
                "description": "這是一場適合新手與親子一起參加的輕鬆交流。會介紹孔雀魚品系、飼育水質、餵食與日常照護。",
                "image_emoji": "🐠",
                "starts_at": now + timedelta(days=3, hours=2),
                "location": "嘎比嘎比交流區",
                "points_reward": 50,
                "max_capacity": 30,
            },
            {
                "title": "嘎比嘎比會員交流日",
                "slug": "sleepover-aquarium",
                "category": "event",
                "summary": "會員限定交流活動，一起分享養魚心得與繁殖經驗。",
                "description": "嘎比嘎比會員交流日是會員限定活動，包含夜間導覽、海洋故事時間與隔日早餐。適合親子、朋友與喜歡海洋的旅客。",
                "image_emoji": "🌙",
                "starts_at": now + timedelta(days=10, hours=6),
                "location": "會員交流區",
                "points_reward": 120,
                "max_capacity": 20,
            },
            {
                "title": "孔雀魚飼育講座",
                "slug": "sea-turtle-conservation",
                "category": "conservation",
                "summary": "了解孔雀魚飼育、換水節奏、繁殖照護與健康觀察。",
                "description": "由嘎比嘎比團隊分享孔雀魚照護經驗，帶會員認識常見疾病、繁殖環境與日常管理。活動結束後可獲得會員點數。",
                "image_emoji": "🫧",
                "starts_at": now + timedelta(days=7, hours=1),
                "location": "嘎比嘎比教室 A",
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