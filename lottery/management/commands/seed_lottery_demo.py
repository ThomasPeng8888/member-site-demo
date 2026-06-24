from django.core.management.base import BaseCommand

from lottery.models import LotteryPrize


class Command(BaseCommand):
    help = "Create demo lottery prizes for 嘎比嘎比孔雀魚."

    def handle(self, *args, **options):
        prizes = [
            {
                "prize_code": "DRINK_10",
                "prize_name": "飲品折抵 10 元",
                "prize_desc": "嘎比嘎比會員限定小確幸，可於現場消費折抵。",
                "image_emoji": "🧋",
                "weight": 50,
                "stock": None,
                "points_cost": 10,
                "enabled": True,
                "sort_order": 10,
            },
            {
                "prize_code": "FEED_SAMPLE",
                "prize_name": "孔雀魚飼料試用包",
                "prize_desc": "適合新手會員體驗的小份量飼料試用包。",
                "image_emoji": "🐟",
                "weight": 25,
                "stock": 30,
                "points_cost": 10,
                "enabled": True,
                "sort_order": 20,
            },
            {
                "prize_code": "DISCOUNT_50",
                "prize_name": "現場消費折抵 50 元",
                "prize_desc": "可於指定商品或活動消費時使用。",
                "image_emoji": "🎟️",
                "weight": 15,
                "stock": 20,
                "points_cost": 10,
                "enabled": True,
                "sort_order": 30,
            },
            {
                "prize_code": "VIP_DRAW",
                "prize_name": "VIP 特別抽選資格",
                "prize_desc": "獲得一次未來特殊活動的優先抽選資格。",
                "image_emoji": "⭐",
                "weight": 8,
                "stock": 10,
                "points_cost": 10,
                "enabled": True,
                "sort_order": 40,
            },
            {
                "prize_code": "BIG_GIFT",
                "prize_name": "嘎比嘎比神秘大禮",
                "prize_desc": "稀有獎項，請至現場出示兌換碼兌換。",
                "image_emoji": "🎁",
                "weight": 2,
                "stock": 3,
                "points_cost": 10,
                "enabled": True,
                "sort_order": 50,
            },
        ]

        for prize_data in prizes:
            LotteryPrize.objects.update_or_create(
                prize_code=prize_data["prize_code"],
                defaults=prize_data,
            )

        self.stdout.write(self.style.SUCCESS("Lottery demo prizes created."))