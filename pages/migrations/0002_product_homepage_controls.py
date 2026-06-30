from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="homepage_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="數字越小越前面；只影響首頁輪播，不影響商品列表排序。",
                verbose_name="首頁輪播排序",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="show_on_homepage",
            field=models.BooleanField(
                default=False,
                help_text="勾選後會優先出現在首頁上方商品照片輪播，可用首頁輪播排序控制順序。",
                verbose_name="顯示於首頁輪播",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="商品列表排序，數字越小越前面"),
        ),
    ]
