# Generated manually for 嘎比嘎比孔雀魚 campaign feature.

import campaigns.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("campaign_id", models.CharField(default=campaigns.models.generate_campaign_id, max_length=40, unique=True, verbose_name="活動抽獎編號")),
                ("slug", models.SlugField(help_text="例如 guppy-summer-draw，網址會是 /campaigns/guppy-summer-draw/。", max_length=120, unique=True, verbose_name="網址代稱")),
                ("campaign_name", models.CharField(max_length=120, verbose_name="活動抽獎名稱")),
                ("campaign_desc", models.TextField(blank=True, verbose_name="活動說明")),
                ("image_emoji", models.CharField(default="🎉", max_length=10, verbose_name="活動圖示")),
                ("prize_name", models.CharField(max_length=120, verbose_name="獎品名稱")),
                ("prize_desc", models.TextField(blank=True, verbose_name="獎品說明")),
                ("winner_count", models.PositiveIntegerField(default=1, verbose_name="正取名額")),
                ("alternate_count", models.PositiveIntegerField(default=0, verbose_name="候補名額")),
                ("register_start_at", models.DateTimeField(verbose_name="報名開始時間")),
                ("register_end_at", models.DateTimeField(verbose_name="報名截止時間")),
                ("draw_at", models.DateTimeField(blank=True, null=True, verbose_name="預計抽獎時間")),
                ("draw_executed_at", models.DateTimeField(blank=True, null=True, verbose_name="實際抽獎時間")),
                ("eligibility_rule", models.CharField(blank=True, help_text="例如：限嘎比嘎比會員、限完成消費集點會員等。第一版先做文字說明。", max_length=200, verbose_name="資格說明")),
                ("redeem_expire_days", models.PositiveIntegerField(default=30, verbose_name="中獎兌換有效天數")),
                ("notes", models.TextField(blank=True, verbose_name="內部備註")),
                ("auto_draw", models.BooleanField(default=False, verbose_name="是否自動抽獎")),
                ("publish_flag", models.BooleanField(default=True, verbose_name="是否公開顯示")),
                ("status", models.CharField(choices=[("draft", "草稿"), ("published", "公開中"), ("closed", "已截止"), ("drawn", "已抽獎"), ("archived", "已封存")], default="draft", max_length=20, verbose_name="狀態")),
                ("created_by_name", models.CharField(blank=True, max_length=100, verbose_name="建立人員名稱")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="建立時間")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新時間")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_campaigns", to=settings.AUTH_USER_MODEL, verbose_name="建立人員")),
            ],
            options={
                "verbose_name": "活動抽獎",
                "verbose_name_plural": "活動抽獎",
                "ordering": ["-register_start_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="CampaignRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("registered", "已報名"), ("cancelled", "已取消")], default="registered", max_length=20, verbose_name="報名狀態")),
                ("register_time", models.DateTimeField(default=django.utils.timezone.now, verbose_name="報名時間")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="建立時間")),
                ("campaign", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="registrations", to="campaigns.campaign", verbose_name="活動抽獎")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="campaign_registrations", to=settings.AUTH_USER_MODEL, verbose_name="會員")),
            ],
            options={
                "verbose_name": "活動抽獎報名",
                "verbose_name_plural": "活動抽獎報名",
                "ordering": ["-register_time"],
            },
        ),
        migrations.CreateModel(
            name="CampaignWinner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("winner_id", models.CharField(default=campaigns.models.generate_campaign_winner_id, max_length=50, unique=True, verbose_name="中獎編號")),
                ("campaign_name", models.CharField(max_length=120, verbose_name="活動名稱快照")),
                ("prize_name", models.CharField(max_length=120, verbose_name="獎品名稱快照")),
                ("prize_desc", models.TextField(blank=True, verbose_name="獎品說明快照")),
                ("winner_type", models.CharField(choices=[("primary", "正取"), ("alternate", "候補")], default="primary", max_length=20, verbose_name="中獎類型")),
                ("winner_rank", models.PositiveIntegerField(default=1, verbose_name="順位")),
                ("winner_status", models.CharField(choices=[("unredeemed", "未兌換"), ("redeemed", "已兌換"), ("expired", "已過期"), ("void", "已作廢")], default="unredeemed", max_length=20, verbose_name="兌換狀態")),
                ("draw_time", models.DateTimeField(default=django.utils.timezone.now, verbose_name="抽獎時間")),
                ("promoted_at", models.DateTimeField(blank=True, null=True, verbose_name="候補遞補時間")),
                ("redeem_code", models.CharField(default=campaigns.models.generate_campaign_redeem_code, max_length=50, unique=True, verbose_name="兌換碼")),
                ("redeem_qr_payload", models.TextField(blank=True, verbose_name="兌換 QR 內容")),
                ("redeemed_at", models.DateTimeField(blank=True, null=True, verbose_name="兌換時間")),
                ("redeemed_by", models.CharField(blank=True, max_length=100, verbose_name="核銷人員")),
                ("expire_at", models.DateTimeField(default=campaigns.models.default_campaign_winner_expire_at, verbose_name="到期時間")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="建立時間")),
                ("campaign", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="winners", to="campaigns.campaign", verbose_name="活動抽獎")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="campaign_winners", to=settings.AUTH_USER_MODEL, verbose_name="中獎會員")),
            ],
            options={
                "verbose_name": "活動抽獎中獎名單",
                "verbose_name_plural": "活動抽獎中獎名單",
                "ordering": ["campaign", "winner_type", "winner_rank"],
            },
        ),
        migrations.AddConstraint(
            model_name="campaignregistration",
            constraint=models.UniqueConstraint(fields=("campaign", "user"), name="unique_campaign_registration"),
        ),
        migrations.AddConstraint(
            model_name="campaignwinner",
            constraint=models.UniqueConstraint(fields=("campaign", "user"), name="unique_campaign_winner"),
        ),
    ]
