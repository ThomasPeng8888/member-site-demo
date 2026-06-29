首頁商品輪播 Banner 純圖片版

調整內容：
1. 移除首頁輪播 Banner 上的「精選商品 / 分類 / 販售中 / 商品名稱 / 描述 / 價格」文字覆蓋層。
2. 保留商品圖片輪播、自動輪播、左右切換、圓點切換。
3. 保留點擊圖片後跳轉到該商品資訊頁的功能。
4. 只調整 pages/templates/pages/home.html 與 pages/static/pages/css/site.css。
5. 不變更資料表、不變更 R2 設定、不影響會員抽獎與活動抽獎。

測試建議：
python manage.py check
python manage.py runserver
