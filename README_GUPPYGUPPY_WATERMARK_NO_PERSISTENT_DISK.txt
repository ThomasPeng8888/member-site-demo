嘎比嘎比孔雀魚｜GuppyGuppy 浮水印保留版（未啟用 Persistent Disk）

本版目的：
1. 將上一版 Render Persistent Disk / MEDIA_ROOT 環境變數調整還原。
2. MEDIA_URL / MEDIA_ROOT 回到原本 Django media/ 本機儲存邏輯：
   - MEDIA_URL = "/media/"
   - MEDIA_ROOT = BASE_DIR / "media"
3. 保留最新商品圖片功能：
   - 正方形裁切
   - 圖片壓縮
   - 手機版商品圖片顯示修正
   - 浮水印文字為 GuppyGuppy Official
4. 沒有新增資料表，不需要 migrate。

注意：
Render 免費方案沒有 Persistent Disk，因此線上後台上傳的 media 圖片仍可能在 redeploy / restart 後遺失。
若未來正式營運且圖片需要永久保存，建議改用雲端圖片儲存，例如 Cloudinary / S3 / R2。
