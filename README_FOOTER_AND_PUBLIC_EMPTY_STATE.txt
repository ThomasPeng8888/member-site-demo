# Footer 與公開空狀態文案優化

本版調整：

1. 網站 footer 從「© 2026」改為「Since-2020 嘎比嘎比孔雀魚」。
2. 訪客與一般會員看不到「請到 Django 後台新增」這類管理提示。
3. 管理員 / staff 仍可看到後台新增提醒，方便營運維護。
4. 不改資料表，不需要 migrate。

覆蓋後請執行：

```powershell
python manage.py check
python manage.py runserver
```
