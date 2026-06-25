嘎比嘎比孔雀魚 UIUX 品牌版面優化說明

本版重點：
1. 桌機版主內容寬度由 1120px 提升到 1280px / 1360px。
2. 首頁 Hero 改成更接近正式品牌網站的寬版區塊。
3. 會員中心、活動、抽獎、活動抽獎列表改為更舒展的桌機版卡片排列。
4. 店員工具頁維持較適合操作的寬度，不盲目放太寬。
5. 導覽列重新整理成主要連結、我的功能、店員工具，避免登入後連結過多擠在一起。
6. 手機版仍保留漢堡選單與單欄/雙欄 RWD，不影響原本手機操作。

本版沒有修改資料表，覆蓋後不需要 makemigrations / migrate。
建議執行：
python manage.py check
python manage.py runserver

修改檔案：
- pages/templates/pages/base.html
- pages/templates/pages/home.html
- pages/static/pages/css/site.css
