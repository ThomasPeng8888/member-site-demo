# Google / LINE 快速登入設定

這版加入現代化會員快速登入：

- Google 登入：第一次登入會直接使用 Google 已驗證 Email 建立會員。
- LINE 登入：第一次登入會先取得 LINE 身分，再請使用者補填 Email；之後即可直接用 LINE 登入。
- 既有 Email 會員：如果使用同一個 Google Email，系統會自動綁定到原本會員；LINE 則在補填同一個 Email 後綁定。

## Render Environment Variables

Google：

```text
GOOGLE_OAUTH_CLIENT_ID=你的 Google OAuth Client ID
GOOGLE_OAUTH_CLIENT_SECRET=你的 Google OAuth Client Secret
```

LINE：沿用原本 LINE Login 設定：

```text
LINE_LOGIN_CHANNEL_ID=你的 LINE Login Channel ID
LINE_LOGIN_CHANNEL_SECRET=你的 LINE Login Channel Secret
```

## Google OAuth Redirect URI

請在 Google Cloud Console 的 OAuth 2.0 Client 加入：

```text
https://你的正式網址/auth/google/callback/
```

本機測試可以另外加入：

```text
http://127.0.0.1:8000/auth/google/callback/
http://localhost:8000/auth/google/callback/
```

## LINE Login Callback URL

請在 LINE Developers Console 的 LINE Login Channel 加入：

```text
https://你的正式網址/auth/line/callback/
```

原本的 LINE 綁定仍然保留，也請繼續保留：

```text
https://你的正式網址/line/callback/
```

本機測試可另外加入：

```text
http://127.0.0.1:8000/auth/line/callback/
http://127.0.0.1:8000/line/callback/
```

## 新增資料庫欄位

這版新增會員 Google 綁定欄位，需要執行：

```powershell
python manage.py migrate
```

Render Build Command 若已包含 `python manage.py migrate`，線上部署會自動套用。
