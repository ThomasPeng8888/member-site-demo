嘎比嘎比孔雀魚 QR Code 流程說明

本版新增「不直接佔版面、需要時展開」的 QR Code 功能，原本手動輸入邏輯完全保留。

新增功能：
1. 會員中心可展開會員 QR Code
   - 店員用 LINE 掃描後會開啟 /staff/add-points/?keyword=會員編號
   - 店員確認會員後輸入消費金額加點

2. 我的獎品可展開常態抽獎兌換 QR Code
   - 店員用 LINE 掃描後會開啟 /staff/redeem/?code=兌換碼
   - 店員確認獎品後核銷

3. 我的活動抽獎可展開活動兌換 QR Code
   - 店員用 LINE 掃描後會開啟 /staff/campaigns/redeem/?code=活動兌換碼
   - 店員確認活動獎品後核銷

新增網址：
- /member/qr.png
- /my-prizes/<spin_code>/qr.png
- /my-campaigns/winners/<winner_id>/qr.png

安全設計：
- QR Code 只負責快速帶入會員編號或兌換碼。
- 加點、核銷仍然需要店員帳號權限。
- 若店員掃描時尚未登入，系統會先要求登入。
- 會員 QR、獎品 QR、活動 QR 都不改變原本業務邏輯，只新增掃描入口。

部署提醒：
- requirements.txt 新增 qrcode 與 Pillow。
- 本機與 Render 部署時請先 pip install -r requirements.txt。
- 沒有新增或修改資料表，所以不需要 makemigrations / migrate。

測試流程：
1. 會員登入 /dashboard/，展開會員 QR Code。
2. 用 LINE 掃描 QR Code，應開啟店員加點頁並帶入會員。
3. 會員到 /my-prizes/，展開兌換 QR Code。
4. 店員掃描後應開啟核銷查詢頁，仍需按確認核銷。
5. 活動抽獎中獎會員到 /my-campaigns/，展開活動核銷 QR Code。
6. 店員掃描後應開啟活動獎品核銷頁，仍需按確認核銷。
