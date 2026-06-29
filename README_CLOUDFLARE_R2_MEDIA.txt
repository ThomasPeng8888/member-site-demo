# Cloudflare R2 商品圖片儲存設定

本版新增 Cloudflare R2 media storage 支援，讓 Render 免費方案休眠、重啟或重新部署後，商品圖片不會因為存在 Render 暫存 media/ 而消失。

## 保留功能

- 商品圖片正方形裁切
- 商品圖片壓縮
- GuppyGuppy Official 自適應浮水印
- 首頁商品輪播 Banner
- 本機開發仍使用 local media/

## Render Environment Variables

請在 Render Web Service → Environment 新增：

```text
USE_R2_MEDIA=True
R2_BUCKET_NAME=guppyguppy-media
R2_ACCOUNT_ID=你的 Cloudflare Account ID
R2_ENDPOINT_URL=https://你的 Cloudflare Account ID.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://pub-xxxxxxxxxxxxxxxx.r2.dev
R2_ACCESS_KEY_ID=你的 Access Key ID
R2_SECRET_ACCESS_KEY=你的 Secret Access Key
```

注意：`R2_SECRET_ACCESS_KEY` 不要 commit 到 GitHub，也不要貼給其他人，只填在 Render Environment。

## 本機開發

本機不用設定 R2，預設仍會使用：

```text
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
```

## 第一次部署後

原本 Render media/ 裡的圖片不會自動搬到 R2。請進入線上 `/admin/` 重新上傳商品圖片一次，之後圖片就會寫入 R2，後續 Render 休眠、重新部署就不會消失。
