# Pause Legacy Activity Registration Module

本版將舊的「嘎比嘎比活動 / 活動報名」模組先從前台與 Django Admin 隱藏。

保留：
- 會員抽獎
- 活動抽獎（campaigns app）
- 我的活動抽獎
- 點數紀錄
- 店員加點
- Cloudflare R2 商品圖片儲存

調整：
- 主選單「活動專區」移除「活動資訊」
- /activities/、/activities/<slug>/、/activities/<slug>/join/ 會導向活動抽獎頁
- 會員資料頁移除「已報名活動」與「推薦活動」
- 會員資料頁新增常用功能卡片：會員抽獎 / 活動抽獎 / 我的活動抽獎
- 首頁會員中心說明移除票券與舊活動報名文案
- Sitemap 移除舊活動資訊 URL，robots.txt 排除 /activities/
- Django Admin 隱藏「嘎比嘎比活動」與「活動報名」

安全策略：
- 不刪 model
- 不刪 migration
- 不刪資料表
- 不清除既有資料

未來若要恢復活動報名，只要恢復 admin / nav / views / dashboard 模板即可，不需要資料庫還原。
