---
name: bimteki-coverage-review-table
description: 在 BIMTeki 專案中生成「建蔽率檢討」表格（表格標題為「建築面積檢討」，俗稱建蔽率檢討表／建築面積檢討表，常見於建照圖說 A0-03）。當使用者想要「做建蔽率檢討表 / 建立建築面積檢討 / 產生建蔽率檢討 / 建蔽率 vs 建築面積檢討 / coverage ratio review table / building coverage review table」時務必使用本 skill，即使沒有明講「skill」二字。左欄為項目標籤（加全形冒號、不加編號），右欄／各分區欄綁 autotext 由 BIMTeki 即時計算、不寫死。**先依 `get_project_core_snapshot` 的 `land.parcels` 數量分兩種版面**：單一使用分區→兩欄式（項目／值）；多個使用分區→陣列欄向版面（每分區一欄＋陣列自帶總計欄，因 BIMTeki 無 per-分區 scalar token，各分區值只能靠陣列 `LandParcel.Parcels`＋`fieldsOrientation:1` 展開）。列組成：基地面積、扣除項（保留地／道路退縮地／鄰房侵占／騎樓，面積>0 才顯示；騎樓地另需勾選「建蔽率計算時騎樓地從基地母數扣除」）、使用面積、法定建蔽率、（多分區另有允建建築面積）、設計建築面積、建蔽率檢討。用 get_project_autotext_catalog(siteOverview,coverage,arrayField)、evaluate_autotext_values(category="coverage,siteOverview")、get_project_core_snapshot 取值判斷，create_project_table_template 一步建表（含合併/框線/等寬）、必要時 modify_project_table_template 修正並讀回驗證。本 skill 只負責「建蔽率檢討表（建築面積檢討）」；各層樓地板面積總表、各層容積檢討、基地概要、建照審查、土管、無障礙、綠化面積、容積區域繪製另有各自的 skill，不要用本 skill 處理。
---

# BIMTeki 建蔽率檢討表生成（表格標題「建築面積檢討」）

在目前開啟的 BIMTeki 專案中，建立一份「建蔽率檢討」表格樣板（表格內大標題為 **建築面積檢討**，A0-03 常見）。把基地面積 → 逐項扣除 → 使用面積（建蔽率分母）→ 法定建蔽率 → 設計建築面積（分子）→ 建蔽率檢討，濃縮成一張速覽表。

**本表有兩種版面，先判斷使用分區數再決定**（`get_project_core_snapshot` 的 `land.parcels` 陣列長度）：

- **單一使用分區 → 兩欄式**（項目／內容）。
- **多個使用分區 → 陣列欄向版面**（項目｜各分區欄｜總計；用一個陣列自動文字展開分區欄）。

左欄一律是**項目標籤＋全形冒號「：」，不加編號**（如「基地面積：」）。右欄／各分區欄的值**一律用 autotext 綁定、由 BIMTeki 即時計算——絕不把讀到的數字寫死**。

逐列規格、display→token 對照、陣列欄位清單，**以 `references/items.md` 為準**；本檔描述流程與兩種版面的組法。

> 需求前提：本 skill 需連上使用者本機的 Archicad + BIMTeki Studio 才能實際執行。

## 前置檢查

1. `bimteki:check_connection`。多開時先 `bimteki:list_archicad_instances` 讓使用者確認要操作哪個專案，再 `bimteki:set_active_archicad_instance` 選定（多開時未選定，其他工具會回報「偵測到多個 instance」錯誤）。
2. `bimteki:get_project_status`（唯讀、成本低）確認專案狀態：`finalized`（已定案）、`project_file.hasFile`（false＝專案只在記憶體中、變更無法落地，請使用者先另存新檔）。回報未開啟 BIMTeki 專案就詢問路徑並 `bimteki:open_bimteki_project` 開啟後重試。
3. 動手前讓使用者知道即將建立的樣板名稱（預設「建蔽率檢討」）。若使用者開著表格編輯器等模態視窗，MCP 會回報 modal dialog 錯誤——請他關掉再繼續。

## 蒐集專案資訊 → 決定版面與顯示哪些列

呼叫 `bimteki:get_project_core_snapshot`：

- **使用分區數**：`land.parcels` 長度。>1 → 多分區版面；=1 → 單分區版面。
- **各扣除項面積**（判斷扣除列是否顯示，>0 才放）：`land.areas` 的 `reserved_area`(保留地)、`road_reserved_area`(道路退縮地)、`neighbor_reserved_area`(鄰房侵佔)、`arcade_area`(騎樓)、`arcade_empty_area`(騎樓地)。
- **騎樓地扣除設定**：`review_settings.minus_arcade_from_site.value`（布林；label「建蔽率計算時騎樓地從基地母數扣除」）。**騎樓地列只有「面積>0 且此設定為真」才顯示**；讀不到就問使用者，不要臆測。
- 基地面積 `site_area`、使用面積(建蔽率用) `using_area_arch`（已扣鄰房侵佔者）。

固定顯示列：基地面積、使用面積、法定建蔽率、設計建築面積、建蔽率檢討（多分區另有允建建築面積）。

## 取得 autotext token

呼叫 `bimteki:get_project_autotext_catalog(category="siteOverview,coverage")`（多分區另加 `arrayField`）。**分類重點**：

- 基地面積與各扣除項面積 token 在 **`siteOverview`**（path「基地概要/土地面積」），display 帶「總計」後綴：`面積：基地面積總計`、`面積：保留地面積總計`、`面積：道路退縮地面積總計`、`面積：鄰房侵佔面積總計`、`面積：騎樓面積總計`、`面積：騎樓地面積總計`。
- 使用面積(建蔽率用)、設計建築面積、建蔽率各式在 **`coverage`**（path「建蔽率相關」）：`面積：使用面積(建蔽率用)總計`、`計算式：使用面積(建蔽率用)總計計算式`、`比率：基準建蔽率`、`計算式：基準建蔽率計算式(不同使用分區時)`、`面積：設計建築面積`、`計算式：設計建蔽率計算式`、`計算式：設計建蔽率檢討式`。
- 多分區的各分區值在 **`arrayField`** 的陣列 `LandParcel.Parcels`（display「土地資訊表-列出使用分區」）。

**格式眉角**：`面積：…` token 放置後**只渲染純數字、不帶單位** → 面積值格用 `segments=[{autotext},{text "m²"}]` 補 `m²`。`計算式：…` token 已是完整字串（含運算符/=/結果、多含 m² 或 %）→ 綁 autotext、不再補文字。

> Token 是欄位識別碼，實測跨專案為同一組 hash（例如 `面積：基地面積總計`＝`${TJL$F8DBE46AB467C}`），但**仍以每個專案 catalog 回傳的 display 比對後取用為準**，不要憑記憶硬編。完整對照見 `references/items.md`。

## 版面 A：單一使用分區（兩欄式）

列（標題 + 依序）：

1. **標題**「建築面積檢討」：`textbold:true`、`textsize:1`、`alignment:1`（靠左）；modify 以 `merges=[{row:0,col:0,colspan:2}]` 跨兩欄。
2. **基地面積：** `面積：基地面積總計` ＋ `m²`。
3. **扣除列（條件顯示）**：保留地／道路退縮地／鄰房侵佔／騎樓／騎樓地，各 `面積：…總計` ＋ `m²`；依上面規則面積>0（騎樓地另需設定）才放。
4. **使用面積：** `面積：使用面積(建蔽率用)總計` ＋ `m²`。**單分區務必用這個純面積 token**——實測 `計算式：使用面積(建蔽率用)總計計算式` 在單分區無扣除時會渲染成壞掉的 `0.00m²`（只有多分區才正常）。
5. **法定建蔽率：** `比率：基準建蔽率`（如 `60%`）。
6. **設計建築面積：** `面積：設計建築面積` ＋ `m²`。
7. **建蔽率檢討：** `計算式：設計建蔽率計算式` ＋ 文字「，」＋ `計算式：設計建蔽率檢討式`（如 `198.33/330.58=59.99%，59.99%≤60% 符合規定...OK!`）；`newline:2`。

建表：`create_project_table_template` 送 cells → `modify_project_table_template` 補 `template_name`、`merges`(標題)、`column_widths=[220,680]`、**`equal_col=[0,0]`**、全格線（見下）。

## 版面 B：多個使用分區（陣列欄向）

模板 **3 欄**：col0＝項目標籤、col1＝陣列根、col2＝**最右空錨欄**。放置後陣列把 col1 往右展開成各分區欄＋陣列自帶「總計」欄，col2 被推到最右當合併錨點。

- **陣列根**（放 col1、欄頭列）：`is_array_autotext_root:true`，`originaldata` 為
  `ARRAY_AUTOTEXT_V1:{"sourceAutoTextToken":"LandParcel.Parcels","columnSettings":[…],"fieldsOrientation":1,"targetType":-858993460,"needGUID":false,"propSettingName":"","isTemplateGUID":false,"targetGUID":""}`；`roomGuid` 常數 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`、`storyGuid` 用全案總計。
  - **`fieldsOrientation:1`** ＝ 欄位排成列、分區排成欄（實測：分區確實變成欄、列數不被撐開）。
  - **可見欄位（columnSettings，依序＝由上而下的列）**：`使用分區`(表頭列)、`土地面積`、有值(>0)的扣除項 `保留地面積`／`道路退縮地`／`鄰房侵占`／`騎樓`／`騎樓地`、`使用面積(建蔽用)計算式`、`基準建築面積計算式`（＝允建建築面積，置於使用面積後）。**欄位名逐字對**（陣列裡是「鄰房侵**占**」「使用面積(建蔽**用**)」）。
  - **陣列自帶「總計」欄**（自動附加，不在 columnSettings 內）→ **不要另加小計欄**；此總計欄即合計。
- **col0 標籤**（與陣列欄位列一一對齊，逐列）：項目／基地面積：／〔扣除列〕／使用面積：／允建建築面積：。
- **底部全案列**（在陣列列之後，非陣列）：法定建蔽率：／設計建築面積：／建蔽率檢討：。每列標籤在 col0、值在 col1、**`merges` 設 col1..col2**——展開後值會橫跨各分區欄＋總計欄（空錨欄提供合併右端點）。
  - 法定建蔽率： `計算式：基準建蔽率計算式(不同使用分區時)`（如 `478.23/726.65=65.81%`）。
  - 設計建築面積： `面積：設計建築面積` ＋ `m²`。
  - 建蔽率檢討： `計算式：設計建蔽率計算式` ＋「，」＋ `計算式：設計建蔽率檢討式`。
- **標題** 跨全寬：`merges` col0..col2。
- **一張表只能有一個陣列自動文字**；本版就這一個。
- 逐列與 columnSettings 完整清單見 `references/items.md`。

**陣列列與 col0 標籤的對齊**：陣列根在欄頭列，其欄位由該列起**逐列往下佔用已存在的列**（不是插入/推擠）——所以要**先把每個陣列欄位對應的列（col0 給標籤、col1 留空）都備好**，列數＝可見欄位數；底部全案列緊接其後。新增/移除陣列欄位時，記得同步增減對應的 col0 標籤列。

## 建表流程（兩版共通）

1. **組 cells**：每格明確給 `newline`（create 對未指定 `newline`/`charwidth` 的格會預設 `charwidth:1` 縮減字寬）。全部 `alignment:1`（靠左，含標題）。
2. `create_project_table_template`，**一次帶齊 `cells`、`merges`、`equal_col`、全格線**（v0.7.1 起 create 已支援 `merges` / `equal_col` / `right_line` / `bottom_line` / `left_line` / `top_line`，不必再「先建再 modify 補」）。取回傳 `nodeGuid`。
   - **合併只能用 `merges` 參數**；寫在 cell 上的 `rowspan`/`colspan` 建立時仍會被忽略。
   - **`equal_col=[0,0]`**：新建表格預設 `equalCol=[0,1…]`（強制等寬）會蓋掉 `column_widths`，用非空的單欄群組 `[0,0]` 解除。
   - **格線**：明確帶 `left_line`（每列 1）、`top_line`（每欄 1）、`right_line`／`bottom_line`（每列×每欄全 1）把整表框滿。
3. `modify_project_table_template` 補上 create 收不到的樣板層級屬性：`template_name`（同名已存在加日期後綴）、`column_widths`、`table_type="normal"`。
   - 步驟 4 讀回若發現 `equalCol` 仍是 `[0,1…]`，在此補傳 `equal_col=[0,0]`。**舊版實測傳 `equal_col=[]`（空陣列）不生效**（被當成未提供）→ 一律用 `[0,0]`，別傳空陣列。
   - **團隊協作要注意**：modify 前會先整批保留所有已放置的表格；若有表格被其他使用者保留，會回傳錯誤與 `lockedTables`（含 templateName／windowTitle／owner）**且不做任何修改** → 把清單轉告使用者，請持有者釋放後再重試。
4. **驗證**：`get_project_table_templates(template_guid=新guid)` 讀回核對列/欄數、標籤文字、各格 token、merges、`equalCol` 應為 `[0,0]`。
   - **未放置到圖面**時陣列不展開、`statedata` 顯示原始 token（正常）；要看實際值用 **`evaluate_autotext_values(category="coverage,siteOverview")`**（通用版；`evaluate_story_autotext_values` 只涵蓋 storyArea，對本表的 token 會回空且不報錯），要看展開版面須放到 layout。
5. **回報**：說明版面（單/多分區）、顯示了哪些扣除列、各列綁的 token、以及**多分區因 MCP 讀不到陣列展開後的儲存格文字，請使用者放到圖面目視確認**分區表頭與各值。

## 已知限制（多分區，需外掛端處理）

- **陣列展開欄的內部直向格線畫不出來**：框線以「模板欄」索引儲存，陣列展開時新插入的分區欄沒有框線資料，故分區欄之間沒有直線（外緣線、col0／錨欄框線正常）。模板層無法為尚不存在的欄預先指定框線；需外掛端在「欄向展開時把陣列根欄的框線複製到新欄」才能補。建表時仍把陣列範圍框線指定滿，讓外掛有資料可複製。
- **陣列自帶「總計」欄無法用 MCP 關閉**；因此不要再自加小計欄（會重複）。

## 注意事項

- **絕不手算寫死**：即使當下能讀到數字算出結果，也一律綁 autotext，讓專案改動後表格跟著更新。
- **條件顯示是關鍵**：扣除列依面積>0（騎樓地另需設定）決定顯示，表格結構因專案而異；只放要顯示的列，別留整列 0 的空扣除項。
- **單分區使用面積用純面積 token、不用計算式**（計算式在單分區會壞成 0.00m²）。
- **不可捏造**：騎樓地扣除設定讀不到就問使用者；外部/行政資訊留佔位符。
- **扣除項數值不對時不要在表格裡硬改**：保留地／道路退縮地／道路退縮地(計入法空)／鄰房侵占屬專案資料，有 `bimteki:set_land_deduction_areas` 可逐分區寫回，但**僅限「扣除項使用者自訂」模式**（`get_project_core_snapshot` 的 `land.is_user_define_reserved_area` 為 true，且各 `land.parcels[].deductions` 的 `writable` 為 true）；預設的「由區域推導」模式下寫進去會被下次重算清掉，工具會直接拒絕，而且**不會代為切換模式**——必須由使用者自己到土地資訊設定切換。騎樓面積／騎樓樓地面積兩種模式下都由建築面積區域重建，屬純計算值、不可寫。
- 新建樣板會寫入專案並存檔；刪除舊樣板（`manage_project_table_templates` delete）須先取得使用者明確同意。已放置的表格 delete 後會轉為靜態表格（不會從圖面移除），圖面物件需使用者自行刪。
