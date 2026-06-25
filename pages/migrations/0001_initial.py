# Generated for official website content IA polish.

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NewsPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='消息標題')),
                ('slug', models.SlugField(max_length=140, unique=True, verbose_name='網址代稱')),
                ('category', models.CharField(choices=[('news', '最新消息'), ('arrival', '新品到貨'), ('care', '飼育知識'), ('event', '活動公告'), ('store', '店鋪公告')], default='news', max_length=30, verbose_name='消息分類')),
                ('summary', models.CharField(max_length=220, verbose_name='消息摘要')),
                ('content', models.TextField(verbose_name='消息內容')),
                ('cover_emoji', models.CharField(default='🐟', help_text='前台卡片使用的小圖示，例如 🐟、✨、📣。', max_length=12, verbose_name='列表圖示')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='是否置頂')),
                ('is_published', models.BooleanField(default=True, verbose_name='是否公開')),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='發布時間')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
            options={
                'verbose_name': '最新消息',
                'verbose_name_plural': '最新消息',
                'ordering': ['-is_pinned', '-published_at', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='商品名稱')),
                ('slug', models.SlugField(max_length=140, unique=True, verbose_name='網址代稱')),
                ('category', models.CharField(choices=[('guppy', '孔雀魚'), ('feed', '飼料與營養'), ('equipment', '水族用品'), ('service', '服務與套組'), ('other', '其他商品')], default='guppy', max_length=30, verbose_name='商品分類')),
                ('short_description', models.CharField(max_length=220, verbose_name='商品簡介')),
                ('description', models.TextField(verbose_name='商品說明')),
                ('image', models.ImageField(blank=True, help_text='目前前台先顯示一張主圖。建議上傳橫式或方形清晰照片。', upload_to='products/', verbose_name='商品圖片')),
                ('price_label', models.CharField(blank=True, help_text='例如：現場洽詢、NT$ 350、依尺寸報價。', max_length=60, verbose_name='價格文字')),
                ('status', models.CharField(choices=[('available', '販售中'), ('limited', '限量 / 預約'), ('sold_out', '暫售完'), ('hidden', '不顯示')], default='available', max_length=30, verbose_name='商品狀態')),
                ('is_featured', models.BooleanField(default=False, verbose_name='首頁精選')),
                ('is_published', models.BooleanField(default=True, verbose_name='是否公開')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序，數字越小越前面')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '我的商品',
                'ordering': ['sort_order', '-is_featured', '-created_at', '-id'],
            },
        ),
        migrations.CreateModel(
            name='StoreInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='嘎比嘎比孔雀魚', max_length=120, verbose_name='店鋪名稱')),
                ('tagline', models.CharField(blank=True, default='專注孔雀魚選育、交流與會員服務的水族工作室。', max_length=160, verbose_name='店鋪短標語')),
                ('intro', models.TextField(verbose_name='店鋪介紹')),
                ('address', models.CharField(blank=True, max_length=220, verbose_name='地址')),
                ('business_hours', models.TextField(blank=True, verbose_name='營業時間')),
                ('phone', models.CharField(blank=True, max_length=60, verbose_name='聯絡電話')),
                ('line_url', models.URLField(blank=True, verbose_name='LINE 官方帳號網址')),
                ('facebook_url', models.URLField(blank=True, verbose_name='Facebook / 社群網址')),
                ('google_map_url', models.URLField(blank=True, verbose_name='Google Map 連結')),
                ('note', models.TextField(blank=True, verbose_name='到店提醒 / 補充說明')),
                ('is_primary', models.BooleanField(default=False, verbose_name='主要店鋪')),
                ('is_published', models.BooleanField(default=True, verbose_name='是否公開')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序，數字越小越前面')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
            options={
                'verbose_name': '店鋪資訊',
                'verbose_name_plural': '店鋪資訊',
                'ordering': ['sort_order', '-is_primary', 'name'],
            },
        ),
    ]
