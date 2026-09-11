---
name: table-area-rooftop
description: 在 BIMTeki 專案中生成「屋突面積檢討」表格（TableTemplate 表格樣板，俗稱屋突X層面積檢討）。當使用者說「做屋突面積檢討表 / 建立屋突檢討 / 產生屋突面積表 / rooftop area review table」，或由 `table-area` skill 帶 `rooftop` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。兩欄式固定四列（標題／屋突面積／允建屋突面積／檢討），三個值欄全用 story 相依 autotext，故各案型共用一份「單一 story-open 樣板」、放置時自選樓層。token 對應、樣板層級設定與腳本用法見本文。各層容積檢討表另有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 屋突面積檢討表生成

在目前開啟的 BIMTeki 專案中，為屋突層建立「屋突面積檢討」表格樣板。
兩欄、固定四列：**標題／屋突面積／允建屋突面積／檢討**。三個值欄一律用**樓層屬性
（story 相依）自動文字**綁定，數值由 BIMTeki 依樓層計算——**絕不把讀到的數字寫死進儲存格**。

結構規格見 `references/table-structure.md`；display→token 對照見 `references/tokens.md`；
儲存格由 `scripts/build_rooftop_table.py` 產生。

## 前置檢查

標準順序與細節見 `references/spoke-conventions.md` 第 1 節，摘要：

1. `bimteki:check_connection`（多開時先選 instance）。**版本關卡**：回傳最後一行「版本：」要看過——沒有這行代表 MCP 早於 0.8.0，照常往下走；需求版本與不足時的處理見 `references/mcp-compat.md`，版本不夠就停手請使用者重跑安裝檔，不要改用舊流程默默建表。
2. `bimteki:get_project_status`：`finalized`／`project_file.hasFile`／`has_unsaved_changes`；未開啟專案就問路徑後 `bimteki:open_bimteki_project` 再重試。
3. **容積區域已匯入**（共用規範第 1 節第 4 步）：`bimteki:get_bimteki_zone_map` 的 `counts.void` 為 0，或 `bimteki:get_project_stories` 的 `blocks[].stories` 沒有該建的樓層，就停手請使用者先自行在 Archicad 繪製容積區域並匯入 BIMTeki；不代畫、不呼叫建立區域的工具、不建表。
4. 動手前告知即將建立的樣板名稱（預設「屋突面積檢討」）與判斷結果，這是寫入專案並存檔的操作；使用者開著表格編輯器等模態視窗時請他先關掉。

本表另外：
- 告知時說明做法（story-open 單一樣板 vs 逐棟多張）與要建幾張。

## 判斷案型與樓層

- `bimteki:get_project_core_snapshot` 讀 `building.case_type`（案型，含 `is_row_house`）、
  `building.block_mode`（單/多棟）與 `story_count.roof`（屋突層數）。
- 多棟時 `bimteki:get_bimteki_block_unit_settings` 取各棟名稱。
- **屋突層用 `bimteki:get_project_stories` 的 `isRoof` 旗標挑**（同時給 `blockName`、`isSumStory`
  與 `guid`，與 `storyGuidList` 是同一組 GUID），比用名稱含「屋突」字串比對可靠；旗標缺漏時才退回
  名稱比對（單棟：屋突X層；多棟分棟：各棟屋突X層；各棟總計：各棟總計屋突X層）。
- `bimteki:get_project_autotext_catalog(category="roofArea,storyArea")` 取 token（見 `references/tokens.md`）。
  **三個值都是 story 相依（targetType=story、needGUID=true）**：屋突面積＝storyArea「算式：室內樓地板面積」
  或「算式：屋突」；允建屋突面積＝roofArea「算式：屋突允建面積」；檢討＝roofArea「算式：屋突檢討式」。

## 決定做幾張表（單一 story-open 樣板優先）

**屋突面積檢討表的三個值都是 story 相依，且單棟／多棟分棟／各棟總計用的自動文字與格式完全相同**，
因此優先做 **單一 story-open 樣板**、放置時自選樓層即可涵蓋全部情形：

1. `build_rooftop_table.py` 給 `story_open:true`；多棟分棟檢討時 `block_prefix:true`（標題加棟別）。
   三個值格預設就綁好（屋突面積、允建屋突面積、屋突檢討式）。
2. `create_project_table_template(cells=..., merges=...)` 建表，取回 `nodeGuid`。
3. `modify_project_table_template(template_guid=新guid, table_type="story", story_guid="",
   column_widths=...)` —— 設樣板層級 **table_type="story"、story_guid=""（清空＝樓層打開）**。
4. 放置表格時由使用者自選樓層，所有 story 相依自動文字（樓層名稱／棟別／室內面積／允建/檢討）
   即依放置樓層與其棟別自動解析。

若使用者偏好每棟每屋突層各一張、各格綁死該層 story：`story_open:false`＋給該屋突層 `story_guid`，
逐棟逐層各建一張（同一組 token 換 storyGuid 即得該層值）。

## 產生儲存格並建表

共通眉角見 `references/spoke-conventions.md` 第 5～6 節；下面只列本表特有的設定。

1. 組 config（欄位見腳本頂註與 table-structure.md），執行 `build_rooftop_table.py` 取 `{cells, merges, column_widths}`。
2. `create_project_table_template(cells=..., merges=...)`——標題跨兩欄的合併直接在此帶。取回傳 `nodeGuid`。
3. `modify_project_table_template(...)` 補 create 收不到的樣板層級屬性：`template_name`、
   `column_widths`；story-open 版在此設 `table_type="story"`、`story_guid=""`（清空＝樓層打開）；
   逐棟版命名「A棟屋突一層面積檢討」等。
4. **驗證**：`get_project_table_templates(template_guid=新guid)` 讀回，核對欄列數、merges、
   各格 originaldata token；story-open 版各格無 storyGuid、樣板層級 tableType 應為 story、story_guid 空；
   逐棟版各格 storyGuid 為該屋突層。
   - 要看實際數值把表格放到某屋突層後再看，或用
     **`evaluate_autotext_values(category="storyArea,roofArea", story_guids=[該屋突層])`**。
     ⚠ **不要用 `evaluate_story_autotext_values`**：它只涵蓋 `storyArea`，本表的允建屋突面積與
     屋突檢討式屬 **roofArea** 分類，用它求值會回空且不報錯（只有屋突面積那格求得到）。

## 儲存格寫法要點

- 標題 `textsize:1`、跨兩欄 colspan 2；其餘 `textsize:2`。全表 `alignment:1`、`textbold:false`、`charwidth:0`；值格 `newline:3`（直接換行）。格式值域見 `references/spoke-conventions.md` 第 5 節。
- 逐棟版每格帶 `storyGuid`（該屋突層）與 `roomGuid`（常數 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`）；
  story-open 版各格不帶 storyGuid，改由樣板層級 `story_guid`（清空＝打開）＋ `table_type="story"` 決定。
- 屋突面積預設「算式：室內樓地板面積」，可用 config `area_token_display` 覆寫為「算式：屋突」。
- 欄寬預設 [220, 616]。

## 注意事項

- 動手前先讓使用者確認做法（story-open 單一 vs 逐棟多張）與樓層範圍。
- roofArea／storyArea token 屬**各案專屬**，務必以 `get_project_autotext_catalog` 重取確認，勿硬編跨案。
