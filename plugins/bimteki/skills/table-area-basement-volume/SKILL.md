---
name: table-area-basement-volume
description: 在 BIMTeki 專案中生成「地下層容積檢討」表格（俗稱地下層免計容積檢討／地下層停車空間容積檢討）。當使用者說「做地下層容積檢討表 / 地下室容積檢討表 / 地下層停車空間容積檢討 / basement volume review table」，或由 `table-area` skill 帶 `basement` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。全案只有一張表（不分棟），上半用陣列自動文字「地下層停車清單」放置時逐樓層展開，其後為小計、防空避難、可扣容積總計與最終檢討列，值一律綁 autotext。欄位組成、腳本與 MCP 呼叫順序見本文。地上層容積、屋突、面積總表另有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 地下層容積檢討表生成

在目前開啟的 BIMTeki 專案中，建立**一張**「地下層容積檢討」表格樣板。這張表**全案只有一張、
不分棟**——地下層停車與免計容積是以全案總量檢討的，所以即使多棟也只做一張（用全案總計脈絡）。

這張表的靈魂是**一個陣列自動文字**：把「地下層停車清單」放進一個儲存格，BIMTeki 在**放置到圖面時**
會自動依專案的停車樓層逐列展開（例：地下二層／地下一層／地上一層），每列填該樓層的欄位值。
你不需要、也不應該自己逐樓層列出——那是陣列的工作。陣列列之下再手動放小計列與檢討區塊。

值欄一律用 autotext 綁定、由 BIMTeki 即時計算——**絕不要把當下讀到的數字寫死進儲存格**。

完整逐列結構規格見 `references/table-structure.md`；display→token 對照與陣列欄位規格見
`references/tokens.md`；儲存格由 `scripts/build_basement_table.py` 產生。本檔描述流程。

## 前置檢查

標準順序與細節見 `references/spoke-conventions.md` 第 1 節，摘要：

1. `bimteki:check_connection`（多開時先選 instance）。**版本關卡**：回傳最後一行「版本：」要看過——沒有這行代表 MCP 早於 0.8.0，照常往下走；需求版本與不足時的處理見 `references/mcp-compat.md`，版本不夠就停手請使用者重跑安裝檔，不要改用舊流程默默建表。
2. `bimteki:get_project_status`：`finalized`／`project_file.hasFile`／`has_unsaved_changes`；未開啟專案就問路徑後 `bimteki:open_bimteki_project` 再重試。
3. **容積區域已匯入**（共用規範第 1 節第 4 步）：`bimteki:get_bimteki_zone_map` 的 `counts.void` 為 0，或 `bimteki:get_project_stories` 的 `blocks[].stories` 沒有該建的樓層，就停手請使用者先自行在 Archicad 繪製容積區域並匯入 BIMTeki；不代畫、不呼叫建立區域的工具、不建表。
4. 動手前告知即將建立的樣板名稱（預設「地下層容積檢討」）與判斷結果，這是寫入專案並存檔的操作；使用者開著表格編輯器等模態視窗時請他先關掉。

本表另外：
- 告知時要列出：即將建一張「地下層容積檢討」表與預設欄位。

## 這張表能不能做／要不要做

- 這張表用的資料（陣列停車清單、地下層總計、可扣容積、防空避難室面積）都是全案層級，
  不分棟、也不逐樓層綁 story，因此**單棟或多棟都一樣做一張**。
- 若專案根本沒有地下層、也沒有任何停車空間，這張表沒有意義；先向使用者確認。

## 決定欄位（陣列的可見欄位）

陣列「地下層停車清單」可用欄位（fieldName 需**逐字**對，見 `references/tokens.md`）：
`樓層／樓地板面積／汽車位數／機車位數／自行車位數／可扣容積計算式`。

- **預設欄位＝`["樓層","汽車位數","機車位數","樓地板面積"]`**（第一欄固定「樓層」，因為陣列根放 col0）。
  這是使用者最常要的版面（對應附圖）。
- 欄數 = 可見欄位數 = 表格總欄數；欄頭列、小計列都依這個順序對齊。
- **自行車位數**：只有專案確實有自行車（腳踏車）停車位時才建議加入。判斷用
  **`bimteki:get_project_parking_info`** 的 `counts.actual_bicycle`（實設自行車位數）或 `basement.total`；
  沒有就別放，以免多一欄空值。
  > **不要用 `evaluate_story_autotext_values`**：它只涵蓋 `storyArea` 分類，拿它評「數量：地下層總計
  > 自行車停車位數」（volumeCheck 分類）會回空、且不報錯，很容易被誤判成 0。真要走 autotext 求值
  > 請用通用版 `bimteki:evaluate_autotext_values(category="volumeCheck")`。
- 使用者有指定就照指定；不確定就用預設、並告知可加/減欄位。

## 取得 token（建議做，勿硬編）

0. `bimteki:get_project_parking_info`（唯讀）：**這張表所有數字的權威來源**。回傳的 `basement`
   就是「地下層停車清單」陣列自動文字背後的資料（逐層 floorId／floorArea／各車種數量／可扣容積
   與算式、`total`、`deductible_volume_total`、`add_volume`），`counts` 則有法定／實設位數。
   陣列自動文字無法求值，需要數字（決定欄位、事後核對展開結果對不對）時就從這裡讀。
   注意：**表格儲存格仍然一律綁 autotext token，不要把這裡讀到的數字寫死進去**——本工具是用來
   判斷與驗證的，不是拿來填表的。
1. `bimteki:get_project_autotext_catalog(category="arrayField")`：確認陣列「地下層停車清單」的
   `token`＝`ParkingInfoStoryManager.ParkingInfoStories`（path：容積檢討/地下層免計容積檢討/地下層停車清單）。
2. `bimteki:get_project_autotext_catalog(category="volumeCheck")`：取小計與檢討區塊 token
   （路徑 `容積檢討/地下層免計容積檢討/總計` 與 `.../檢討`）。回傳很大，建議存檔後用 jq/python 過濾。
3. `bimteki:get_project_autotext_catalog(category="coverage")`：取「面積：法定防空避難室面積」
   （path：建蔽率相關）。
   實測穩定的預設 token 已內建在 build 腳本；**仍建議比對確認**，有出入時放進 config 的 `tokens` 覆寫。
4. **最保險的佐證**：專案的樣板庫常帶一張 sample「地下層容積檢討」——用
   `bimteki:get_project_table_templates` 找到它、讀其 cells，`is_array_autotext_root` 那格的
   `originaldata`（`ARRAY_AUTOTEXT_V1:{...}`）就是陣列欄位的權威寫法，可直接照抄欄位名。

## 決定綁定脈絡（storyGuid / roomGuid）

- 這些 token 多為全案層級（needGUID=false），story 脈絡實務上不影響計算，但為與內建表一致，
  各格仍帶 `storyGuid`＝**全案總計** story guid。取法：`get_project_autotext_catalog` 的
  `storyGuidList` 中，多棟取**最後一個「總計：」**、單棟取其唯一「總計：」。
- `roomGuid` 一律用常數 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`（所有 BIMTeki 容積檢討表都用它，照抄）。

## 產生儲存格並建表

共通眉角見 `references/spoke-conventions.md` 第 5～6 節；下面只列本表特有的設定。

1. 組 `scripts/build_basement_table.py` 的 config JSON：
   ```json
   {
     "story_guid": "全案總計 story guid（含大括號，如 {9768fca4-...})",
     "columns": ["樓層","汽車位數","機車位數","樓地板面積"],
     "include_floor_area_row": false,
     "tokens": { "算式：地下層可扣容積": "${TJL$...}" }
   }
   ```
   執行取得 `{cells, merges, column_widths, cols, rows}`。欄位說明見 `references/table-structure.md`。
2. `bimteki:create_project_table_template(cells=..., merges=..., equal_col=[0,0])`，合併與等寬一併在此帶齊。
   **實測**：create 也能吃 `is_array_autotext_root` ＋ `originaldata`、`segments`、混合文字。取回傳 `nodeGuid`。
3. `bimteki:modify_project_table_template(template_guid=新guid, template_name="地下層容積檢討",
   column_widths=..., table_type="normal")` 補上 create 收不到的樣板層級屬性（樣板名、欄寬、類型）。
   同名已存在時加日期後綴。
   - **等寬**：步驟 2 已帶 `equal_col=[0,0]`；若步驟 4 讀回仍是 `[0,N]`，在此補傳一次 `equal_col=[0,0]`（別傳空陣列）。
4. **驗證**：`bimteki:get_project_table_templates(template_guid=新guid)` 讀回，核對：
   - 陣列根那格仍有 `is_array_autotext_root:true`，`originaldata` 是完整 `ARRAY_AUTOTEXT_V1:{...}`
     且 `columnSettings` 欄位/順序正確。
   - 小計列各欄 originaldata 是正確的「數量/面積：地下層總計…」token；檢討區塊三格 token 正確。
   - merges、cols/rows、column_widths 符合預期。
   - **正常現象**：未放置到圖面的樣板，陣列不會展開、值格 `statedata` 顯示原始 token 字串（尚未評估）。
     要看實際展開（地下二層／…＋計算值）需把樣板放到 layout；**要先確認展開後的內容對不對，
     不必放圖——直接讀 `bimteki:get_project_parking_info` 的 `basement` 逐層明細比對即可**。
     要看單一 token 的數值，用 `bimteki:evaluate_autotext_values(category="volumeCheck")`
     （通用版；`evaluate_story_autotext_values` 只涵蓋 storyArea，對本表的 token 無效）。

## 注意事項

- 動手前讓使用者確認欄位與命名。
- **每張表只允許一個陣列自動文字**（MCP 限制）。本表只用一個（停車清單），勿再加第二個陣列。
- 陣列根固定放在**欄頭列的下一列、col0**；同列其餘欄位放空白佔位格（定義初始欄寬）。放置時陣列
  往下展開、把小計/檢討各列往下推——所以小計列要緊接在陣列根列之後，展開後才會正好接在清單下方。
- 可扣容積算式（算式：地下層可扣容積）由 BIMTeki 依專案資料組成，**會自動含防空避難室、且若有自行車
  也會納入**；不同專案顯示的項數不同是正常的，照綁 token 即可，不要自己改寫算式。
- 若 `get_project_parking_info` 與 `evaluate_autotext_values` 都不可用，不要臆測數值：陣列與各 token
  照綁，並在回報時說明「因數值取得失敗，本次未依 0 值判斷是否加入自行車欄」。
