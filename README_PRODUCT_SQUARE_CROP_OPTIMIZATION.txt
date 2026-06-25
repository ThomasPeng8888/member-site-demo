嘎比嘎比孔雀魚｜商品圖片正方形裁切與壓縮優化

本版針對「商品資訊」圖片做正式網站常見的商品圖處理流程：

1. 後台新增 / 更換商品圖片時，會出現正方形裁切工具。
   - 選擇圖片後會顯示圖片預覽。
   - 可以拖曳白色正方形裁切框調整商品主體。
   - 可以拉右下角圓點調整裁切範圍大小。
   - 右側會顯示前台正方形預覽。

2. 儲存後圖片處理流程：
   - 依後台裁切框裁成 1:1 正方形。
   - 最長邊限制在 1600px 內，避免過大。
   - JPEG 使用 progressive + optimize 並控制品質。
   - PNG / BMP / GIF 等會轉成網站較適合的 JPEG。
   - 套用「嘎比嘎比孔雀魚」品牌浮水印。

3. 前台 UI 統一為正方形商品圖：
   - 商品列表圖片固定 1:1。
   - 首頁精選商品圖片固定 1:1。
   - 商品詳情頁主圖固定 1:1。
   - 浮水印位置因此更一致，商品卡片也更整齊。

4. 中央浮水印微幅加深。
   - 比上一版更容易看見。
   - 仍保持低調，避免破壞魚體顏色與商品視覺。

5. 資料表沒有變更。
   - 不需要 makemigrations。
   - 不需要 migrate。

覆蓋方式：
robocopy D:\member_site_demo_product_square_crop_optimization\member_site_demo D:\member_site_demo /E /XD .git venv staticfiles __pycache__ media /XF db.sqlite3 .env

本機測試：
cd D:\member_site_demo
.\venv\Scripts\Activate.ps1
python manage.py check
python manage.py runserver

Git 推送：
git status
git add .
git commit -m "Add square cropper for product images"
git push

注意：
- 這版不會把圖片二進位存進資料庫；資料庫只保存圖片路徑，實際檔案仍在 media 目錄。
- 若是 Render 免費環境且未設定 Persistent Disk，media 上傳圖片仍可能因環境重建而遺失；正式長期營運建議接 Persistent Disk 或雲端物件儲存。
- 舊圖片若在後台使用「重新套用嘎比嘎比孔雀魚浮水印」，會用中央裁切方式處理，若需要精準構圖，建議重新上傳原圖並用裁切工具調整。
