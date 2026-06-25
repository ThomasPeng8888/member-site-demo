# Mobile Hero RWD Fix

這版修正首頁手機版 Hero 區塊在窄螢幕時，Guppy Membership、主標題、描述文字或 email 可能超出背景模板的問題。

修正重點：

1. 手機版 Hero 恢復為獨立圓角卡片背景。
2. 主標題在手機版縮小並強制限制在容器內。
3. 描述文字與 email 加上 overflow-wrap，避免長字串爆框。
4. 保留桌機版寬版品牌 UI、官方 Logo、QR Code、LINE、抽獎與店員功能。
5. 沒有修改資料表，不需要 migrate。

測試：

```powershell
python manage.py check
python manage.py runserver
```

本機確認後：

```powershell
git add .
git commit -m "Fix mobile homepage hero overflow"
git push
```
