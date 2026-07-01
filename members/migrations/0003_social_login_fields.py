from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0002_line_profile_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberprofile",
            name="google_sub",
            field=models.CharField(blank=True, db_index=True, max_length=255, verbose_name="Google 帳號識別碼"),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="google_email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="Google Email"),
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="google_bound_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Google 綁定時間"),
        ),
        migrations.AddConstraint(
            model_name="memberprofile",
            constraint=models.UniqueConstraint(condition=Q(("google_sub", ""), _negated=True), fields=("google_sub",), name="unique_non_empty_google_sub"),
        ),
    ]
