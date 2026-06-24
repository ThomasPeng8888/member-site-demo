# Generated manually for reward duplicate protection

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aquarium", "0002_staffpointgrant"),
    ]

    operations = [
        migrations.AddField(
            model_name="activityregistration",
            name="reward_granted",
            field=models.BooleanField(default=False, verbose_name="報名點數是否已發放"),
        ),
    ]
