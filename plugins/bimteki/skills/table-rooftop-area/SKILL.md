---
name: table-rooftop-area
description: 在 BIMTeki 專案中生成「屋突面積檢討」表格（TableTemplate 表格樣板，俗稱屋突X層面積檢討，建照圖說 A0-12~14）。當使用者說「做屋突面積檢討表 / 建立屋突檢討 / 產生屋突面積表 / rooftop area review table」，或由 `table` skill 帶 `rooftop` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。兩欄式固定四列（標題／屋突面積／允建屋突面積／檢討），三個值欄全用 story 相依 autotext，故各案型共用一份「單一 story-open 樣板」、放置時自選樓層。token 對應、樣板層級設定與腳本用法見本文。各層容積檢討表另有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 屋突面積檢討表生成

在目前開啟的 BIMTeki 專案中，為屋突層建立「屋突面積檢討」表格樣板。
兩欄、固定四列：**標題／屋突面積／允建屋突面積／檢討**。三個值欄一律用**樓層屬性
（story 相依）自動文字**綁定，數值由 BIMTeki 依樓層計算——**絕不把讀到的數字寫死進儲存格**。

結構規格見 `references/structure.md`；display→token 對照見 `references/tokens.md`；
儲存格由 `scripts/build_rooftop_table.py` 產生。

## 前置檢查

1. `bimteki:check_connection`。多開時先 `bimteki:list_archicad_instances` 讓使用者確認，
   再 `bimteki:set_active_archicad_instance` 選定，或每次帶 `target_port`。
   **版本關卡**：`check_connection` 回傳最後一行「版本：」要看過（**沒有這行代表 MCP 早於 0.8.0，照常往下走、不要擋**）——使用者的 MCP／外掛
   是隨安裝檔更新的，跟本 skill 常常不同期。需求版本與版本不足時的處理方式見
   `../table/references/mcp-compat.md`；版本不夠就停手請使用者重跑安裝檔，
   不要改用舊流程默默把表建出來（使用者會拿到一張跟預期不同的表卻不知道為什麼）。
2. `bimteki:get_project_autotext_catalog(category="roofArea")` 與 `(category="storyArea")`
   取 token（見 tokens.md）。**三個值都是 story 相依（targetType=story、needGUID=true）**：
   屋突面積＝storyArea「算式：室內樓地板面積」或「算式：屋突」；
   允建屋突面積＝roofArea「算式：屋突允建面積」；檢討＝roofArea「算式：屋突檢討式」。
3. `bimteki:get_project_status`（唯讀、成本低）確認 `finalized`（已定案）與 `project_file.hasFile`
   （false＝專案只在記憶體中、變更無法落地，請使用者先另存新檔）。
4. 動手前告知使用者：即將建幾張表、做法、會寫入專案並存檔。
   若 Archicad 開著模態視窗（如「設定」），MCP 會回 modal dialog 錯誤——請使用者關掉再繼續。

## 判斷案型與樓層

- `bimteki:get_project_core_snapshot` 讀 `building.case_type`（案型，含 `is_row_house`）、
  `building.block_mode`（單/多棟）與 `story_count.roof`（屋突層數）。
- 多棟時 `bimteki:get_bimteki_block_unit_settings` 取各棟名稱。
- **屋突層用 `bimteki:get_project_stories` 的 `isRoof` 旗標挑**（同時給 `blockName`、`isSumStory`
  與 `guid`，與 `storyGuidList` 是同一組 GUID），比用名稱含「屋突」字串比對可靠；旗標缺漏時才退回
  名稱比對（單棟：屋突X層；多棟分棟：各棟屋突X層；各棟總計：各棟總計屋突X層）。

## 決定做幾張表（單一 story-open 樣板優先）

**屋突面積檢討表的三個值都是 story 相依，且單棟／多棟分棟／各棟總計用的自動文字與格式完全相同**，
因此優先做 **單一 story-open 樣板**、放置時自選樓層即可涵蓋全部情形：

1. `build_rooftop_table.py` 給 `story_open:true`；多棟分棟檢討時 `block_prefix:true`（標題加棟別）。
   三個值格預設就綁好（屋突面積、允建屋突面積、屋突檢討式）。
2. `create_project_table_template(cells=...)` 建表，取回 `nodeGuid`。
3. `modify_project_table_template(template_guid=新guid, table_type="story", story_guid="",
   merges=..., column_widths=...)` —— 設樣板層級 **table_type="story"、story_guid=""（清空＝樓層打開）**。
4. 放置表格時由使用者自選樓層，所有 story 相依自動文字（樓層名稱／棟別／室內面積／允建/檢討）
   即依放置樓層與其棟別自動解析。

若使用者偏好每棟每屋突層各一張、各格綁死該層 story：`story_open:false`＋給該屋突層 `story_guid`，
逐棟逐層各建一張（同一組 token 換 storyGuid 即得該層值）。

## 產生儲存格並建表

1. 組 config（欄位見腳本頂註與 structure.md），執行 `build_rooftop_table.py` 取 `{cells, merges, column_widths}`。
2. `create_project_table_template(cells=..., merges=...)`——v0.7.1 起 create 已支援 `merges` /
   `equal_col` / 框線參數，標題跨兩欄的合併直接在此帶（cell 上的 `rowspan`/`colspan` 仍然無效）。
   取回傳 `nodeGuid`。
3. `modify_project_table_template(...)` 補 create 收不到的樣板層級屬性：`template_name`、
   `column_widths`；story-open 版在此設 `table_type="story"`、`story_guid=""`（清空＝樓層打開）；
   逐棟版命名「A棟屋突一層面積檢討」等。
   - **團隊協作要注意**：modify 前會先整批保留所有已放置的表格；若有表格被其他使用者保留，會回傳
     錯誤與 `lockedTables`（含 templateName／windowTitle／owner）**且不做任何修改** → 把清單轉告
     使用者，請持有者釋放後再重試。
4. **驗證**：`get_project_table_templates(template_guid=新guid)` 讀回，核對欄列數、merges、
   各格 originaldata token；story-open 版各格無 storyGuid、樣板層級 tableType 應為 story、story_guid 空；
   逐棟版各格 storyGuid 為該屋突層。
   - 未放置的樣板 `statedata` 顯示原始 token（尚未評估），核對以 `originaldata` 為準；
     要看實際數值把表格放到某屋突層後再看，或用
     **`evaluate_autotext_values(category="storyArea,roofArea", story_guids=[該屋突層])`**。
     ⚠ **不要用 `evaluate_story_autotext_values`**：它只涵蓋 `storyArea`，本表的允建屋突面積與
     屋突檢討式屬 **roofArea** 分類，用它求值會回空且不報錯（只有屋突面積那格求得到）。

## 儲存格寫法要點

- 標題 `textsize:1`、跨兩欄 colspan 2；其餘 `textsize:2`。全表 `alignment:1`、`textbold:false`、`charwidth:0`；值格 `newline:3`。
- 逐棟版每格帶 `storyGuid`（該屋突層）與 `roomGuid`（常數 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`）；
  story-open 版各格不帶 storyGuid，改由樣板層級 `story_guid`（清空＝打開）＋ `table_type="story"` 決定。
- 屋突面積預設「算式：室內樓地板面積」，可用 config `area_token_display` 覆寫為「算式：屋突」。
- 欄寬預設 [220, 616]。

## 注意事項

- 本 skill 會**新建樣板並存檔**（可逆性低）；動手前先讓使用者確認做法（story-open 單一 vs 逐棟多張）與樓層範圍。
- 刪除舊樣板（`manage_project_table_templates` 的 delete）必須先取得使用者明確同意；已放置到圖面者，刪樣板後圖面元素需人工移除。
- roofArea／storyArea token 屬**各案專屬**，務必以 `get_project_autotext_catalog` 重取確認，勿硬編跨案。
