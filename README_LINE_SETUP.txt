嘎比嘎比孔雀魚 LINE 綁定設定筆記
================================

Render Environment Variables 建議設定：

SITE_URL=https://member-site-demo.onrender.com
LINE_LOGIN_CHANNEL_ID=<LINE Login Channel ID>
LINE_LOGIN_CHANNEL_SECRET=<LINE Login Channel Secret>
LINE_LOGIN_BOT_PROMPT=normal
LINE_MESSAGING_CHANNEL_ACCESS_TOKEN=<Messaging API Channel access token>
LINE_WEBHOOK_CHANNEL_SECRET=<Messaging API Channel secret>
CSRF_TRUSTED_ORIGINS=https://member-site-demo.onrender.com

LINE Developers Console：

1. LINE Login channel
   - App type: Web app
   - Callback URL:
     https://member-site-demo.onrender.com/line/callback/
   - Scope: profile openid

2. Messaging API channel / Official Account
   - Webhook URL:
     https://member-site-demo.onrender.com/line/webhook/
   - Enable webhook
   - Copy Channel access token to LINE_MESSAGING_CHANNEL_ACCESS_TOKEN
   - Copy Channel secret to LINE_WEBHOOK_CHANNEL_SECRET

建議 LINE Login channel 與 Messaging API channel 放在同一個 LINE Provider 底下，
這樣會員透過 LINE Login 取得的 LINE User ID 才能用於官方帳號通知。

本機測試：

python manage.py migrate
python manage.py check
python manage.py runserver

線上綁定頁：

https://member-site-demo.onrender.com/line/settings/

測試推播：

python manage.py test_line_push <會員編號或Email> "嘎比嘎比孔雀魚 LINE 測試成功"
