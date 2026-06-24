from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="memberprofile",
            options={"verbose_name": "會員資料", "verbose_name_plural": "會員資料"},
        ),
        migrations.AlterField(
            model_name="memberprofile",
            name="line_user_id",
            field=models.CharField(blank=True, db_index=True, max_length=100, verbose_name="LINE User ID"),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="line_display_name",
            field=models.CharField(blank=True, max_length=100, verbose_name="LINE 顯示名稱"),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="line_picture_url",
            field=models.URLField(blank=True, max_length=500, verbose_name="LINE 頭像網址"),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="line_bound_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="LINE 綁定時間"),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="line_notify_enabled",
            field=models.BooleanField(default=True, verbose_name="啟用 LINE 通知"),
        ),
        migrations.AddConstraint(
            model_name="memberprofile",
            constraint=models.UniqueConstraint(condition=Q(("line_user_id", ""), _negated=True), fields=("line_user_id",), name="unique_non_empty_line_user_id"),
        ),
    ]
