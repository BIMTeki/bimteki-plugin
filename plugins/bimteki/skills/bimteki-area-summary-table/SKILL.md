---
name: bimteki-area-summary-table
description: 在 BIMTeki 專案中生成「各層樓地板面積」面積總表（TableTemplate 表格樣板，建照圖說 A0-01）。當使用者說「生成面積總表 / 建立各層樓地板面積表 / 做容積面積表格 / area summary table」，或由 `table` skill 帶 `area` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。會先取案型（單棟／一般多棟／連棟透天）再組欄位與樓層列，值一律綁 autotext 由 BIMTeki 即時計算、不寫死；案型分支、騎樓列、0 值欄移除與 MCP 呼叫順序見本文。本 skill 只做面積總表；其他檢討表與容積區域繪製各有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 面積總表生成

在目前開啟的 BIMTeki 專案中，建立一份「各層樓地板面積」表格樣板。表格內容全部使用**自動文字（autotext）**綁定，數值由 BIMTeki 即時計算，不要把當下讀到的數字寫死進儲存格。

欄位與樓層列會**依案型動態調整**，一切列/欄配置、過濾規則與合併算法以 `references/table-structure.md` 為準；本檔描述流程，細節到參考檔查。

## 前置檢查

1. 呼叫 `bimteki:check_connection` 確認與 Archicad / BIMTeki Studio 的連線。
   **版本關卡**：`check_connection` 回傳最後一行「版本：」要看過（**沒有這行代表 MCP 早於 0.8.0，照常往下走、不要擋**）——使用者的 MCP／外掛
   是隨安裝檔更新的，跟本 skill 常常不同期。需求版本與版本不足時的處理方式見
   `../table/references/mcp-compat.md`；版本不夠就停手請使用者重跑安裝檔，
   不要改用舊流程默默把表建出來（使用者會拿到一張跟預期不同的表卻不知道為什麼）。
2. 呼叫 `bimteki:get_project_status`（唯讀、成本低）確認專案狀態：`finalized`（已定案）、`project_file.hasFile`（false＝專案只在記憶體中、變更無法落地，請使用者先另存新檔）。如果回報未開啟 BIMTeki 專案，詢問使用者專案路徑後，用 `bimteki:open_bimteki_project` 協助開啟，再重試。
3. 若使用者有提供範例表格檔案（圖片或 PDF），以該範例的欄位與版面為準來組表；沒有提供時，依 `references/table-structure.md` 的規格生成。

## 判斷案型

呼叫 `bimteki:get_project_core_snapshot`，讀取 `building` 區塊：

- `shared_hall.value`：`true` = 共用梯廳、`false` = 非共用梯廳。**連棟透天案型不適用此概念**（各棟本來就各自獨立出入口），一旦判斷為連棟透天就直接視為非共用梯廳處理，不需再讀這個值。
- `block_mode.value`：`true` = 多棟、`false` = 單棟。
- `block_count.value`：棟數（回報用）。
- `case_type.is_row_house`（或 `case_type.value == "row_house"`）：`true` = 連棟透天（分棟檢討）。此旗標只在多棟案（`block_mode.value == true`）時才有意義。

同一次呼叫順便讀取（供檢討列顯示條件用，見參考檔四之 4）：

- `review_settings.basement_review_mode.value`：`"sum"` = 地下層總量檢討（面板顯示「總量檢討」），其他值 = 分層檢討。
- `building.story_count.basement`：地下層層數（0 = 無地下層）。

先讀 `references/table-structure.md` 的第一～三節。案型共 5 種：單棟(共用/非共用)、一般多棟(共用/非共用) 共 4 種＋連棟透天多棟(固定非共用) 1 種。依 `block_mode` × `case_type.is_row_house` 決定樓層列來源：單棟、一般多棟（有跨棟同層合計）、連棟透天多棟（無跨棟同層合計，各棟分開列示）共 3 種樓層列邏輯；欄位過濾則依「是否非共用梯廳（含連棟透天強制視為非共用）」決定。

**保險檢查**：若 `case_type` 欄位不存在（例如專案資訊面板尚未升級到含此欄位的版本），改用 `bimteki:get_project_stories` 看樓層骨架——多棟時它會回 `blocks`（各棟）與 `totalBlock`（「各棟總計」虛擬棟別，**只有一般多棟才有**；連棟透天沒有）；也可退而查 `get_project_autotext_catalog` 的 `storyGuidList` 有沒有「各棟總計」開頭的節點。仍不確定時，先告知使用者觀察到的樓層結構並詢問案型，不要自行臆測後直接建表。

## 蒐集資料

呼叫 `bimteki:get_project_autotext_catalog` 並指定 `category="storyArea,volumeCheck"`，一次取得：

- **storyArea 分類**（`targetTypeName: "story"`，需要樓層脈絡）：各欄位的 autotext token，例如「樓層名稱」「樓高」「面積：當層樓地板面積」「面積：梯廳」「用途」等。以參考檔第二節每欄的 `display` 名稱比對取 token。
- **volumeCheck 分類**（`targetTypeName: "startmanager"`，不需樓層脈絡）：檢討列 token，例如「允建機電設備空間計算式」「算式：地下室容積檢討式」「計算式：設計容積樓地板面積計算式」等。
- **storyGuidList**：本案樓層清單。單棟為一段樓層＋單一「總計：」；多棟為「A棟各層→總計：→B棟各層→總計：→各棟總計各層→總計：」。樓層列與總計列如何從中挑選，見參考檔第五節。

**Token 是專案特定的，絕對不要憑記憶或從其他專案硬編碼**；一律以 catalog 回傳的 `display` 名稱比對後取用 `token`。

## 決定欄位（過濾）

依 `references/table-structure.md` 第三節，從標準 19 欄依序套用兩道過濾：

1. **非共用過濾**：非共用梯廳時，或案型為連棟透天時（固定視為非共用，不看 `shared_hall.value`），移除 `sharedOnly` 欄（梯廳面積、陽台10%回計、梯廳10%回計、陽台+梯廳15%回計）。
2. **0 值空間欄過濾**：呼叫 `bimteki:evaluate_story_autotext_values`（見參考檔第六節），對「全案總計樓層」取各 `space` 欄的解析後 `value`，為 0（`abs<0.005`）者移除。固定欄（層別、樓高、A、D、用途）一律保留。
   - **若該工具回錯或不可用**：不要用區域圖資硬湊、也不要臆測；改為跳過此道過濾、保留所有（非共用過濾後）欄位，並在最後回報明確告知「因解析數值取得失敗，本次未自動移除 0 欄」。
3. **樓高欄可解析檢查（僅一般多棟）**：一般多棟的樓層列綁「各棟總計XX層」聚合節點，樓高可能解析為 0（聚合節點不會合計樓高，實測「總計：」與夾層小計節點皆回 0）；先用 `evaluate_story_autotext_values` 對各「各棟總計」樓層解析「樓高」，全為 0 或 null 就移除樓高欄（同樣重新編號）並在回報說明。
   - 也可以改用 `bimteki:get_project_stories` 直接看：它逐棟逐層回 `floorHeight`（**單位是公分**，320＝3.2 公尺）與 `isSumStory`，比解析 autotext 直觀；`totalBlock` 底下的總計層樓高本來就不可寫、通常無值。兩種方式擇一即可。單棟與連棟透天的樓層列綁實際樓層、樓高可正常解析，不需此檢查；但凡「小計」「總計」性質的列，樓高格一律留空（見參考檔四之 2）。

過濾後把存活欄**依原順序重新編號**為 0-based col 索引。**連棟透天多棟**在編號前，先在最前面插入固定的「棟別」欄佔掉 col 0（不受上述兩道過濾影響），其餘欄位整體 +1；單棟與一般多棟不插入這一欄。編號完成後算出 `N`、`Dcol`、`firstB/countB`、`firstC/countC`（見參考檔第三節，連棟透天的數值已含棟別欄位移）。之後的 cells / merges / colspan / column_widths 全部以重新編號後的實際索引為準。

## 建表流程

1. **依 `references/table-structure.md` 第四節**組出完整 cells 陣列：標題三列（表頭合併與 colspan 依存活欄動態）、**騎樓列（0~1 列：本案騎樓樓地板面積 > 0 時，插在「地上一層」之前，層別欄固定文字「騎樓」、A 欄綁騎樓 autotext 並把該格 storyGuid 設為地上一層，詳參考檔四之 2）**、樓層列（依案型選 storyGuidList 項目、逐格帶 storyGuid）、總計列（A 欄改綁 buildingOverview 的「計算式：總樓地板面積」以含入騎樓、其餘欄帶全案總計 guid）、檢討列（0～2 列：機電空間容積檢討列僅在全案總計「面積：機電設備」非 0 時顯示；地下層容積檢討列僅在「地下層總量檢討（`basement_review_mode == "sum"`）且地下層面積 > 0」時顯示，詳見參考檔四之 4）、最終列（檢討列與最終列 colspan 依 `Dcol` 計算）。省略檢討列時，後續列的 row 索引與 merges 要跟著上移，不要留空白列。
2. 呼叫 `bimteki:create_project_table_template`，一次傳入所有 cells，**並同時帶 `merges` 與 `equal_col`**（v0.7.1 起 create 已支援 `merges` / `equal_col` / `right_line` / `bottom_line` / `left_line` / `top_line`，這張表合併很多，一步帶齊可省一次大 payload 的往返）。**實測注意**：
   - **合併只能用 `merges` 參數**（清單內容見步驟 3 的說明，兩處是同一份）；寫在 cell 上的 `rowspan` / `colspan` 建立時仍會被忽略。
   - `equal_col: [0, N-1]`（所有欄位同寬儲存格）。
   - create 對未指定的 `charwidth` 預設為 **1（縮減字寬）**，不是 0。因此每一格都要明確給 `charwidth`（數值格、標題列給 0；子欄表頭與 col 0 標籤給 1），否則整張表會被縮減字寬。
3. 從回傳結果取得新樣板的 guid，呼叫 `bimteki:modify_project_table_template` 補上 create 收不到的樣板層級屬性（樣板名、欄寬），以及步驟 4 讀回發現沒吃到的設定：
   - `template_name`：預設「各層樓地板面積」，若同名樣板已存在可加日期後綴避免混淆。
   - **團隊協作要注意**：modify 前會先整批保留所有已放置的表格；若有表格被其他使用者保留，會回傳錯誤與 `lockedTables`（含 templateName／windowTitle／owner）**且不做任何修改** → 把清單轉告使用者，請持有者釋放後再重試。
   - `merges`（若步驟 2 已帶且讀回正確就不必重送；此參數為整組取代）：完整合併清單（大標題 colspan `N`、群組表頭各 rowspan/colspan、B/C 群組表頭 colspan＝存活子欄數、檢討列（如有）colspan `Dcol-1`、最終列 colspan `Dcol+1`；**連棟透天多棟**另外：總計列棟別+層別欄合併 colspan 2、檢討列（如有）的標籤+內容固定合併成一格 colspan `Dcol`、各棟樓層列的棟別欄垂直合併 rowspan＝該棟樓層數+1），此參數為整組取代。
   - `equal_col: [0, N-1]`（所有欄位同寬儲存格；步驟 2 已帶，讀回不對才補送）。
   - `column_widths`：長度 `N`，每欄 100，用途欄（索引 N-1）380；連棟透天的棟別欄（col 0）建議給 60。
   - 若 create 階段有格式沒生效（例如 charwidth），一併在此以 `cells` patch 修正（只帶 row/col 與要改的格式欄位即可，內容會保留）。
   - **若是用 `insert_cols` 在既有樣板前面插入棟別欄**（例如使用者事後才要求加這欄）：這是已知有雷的操作，插入後至少要做兩件事——(a) 讀回 `leftLine`／`rightLine`／`topLine`／`bottomLine`，檢查新欄與相鄰欄之間的框線是否缺漏（常見是整條 0），有缺漏要用 `right_line`／`bottom_line`／`top_line` 補送整組陣列修正；(b) **檢查每一個合併儲存格（尤其是原本錨在 col 0 的大標題 row 0）**，插入後合併儲存格的內容會跟著原欄位一起位移到新的欄位，但 merges 清單的錨點不會自動調整，導致合併範圍左上角是空的、內容整個消失（實測發生過大標題不見）。要用 `cells` patch 把內容搬回新的合併錨點欄，並把原內容所在的欄位清成空字串，讀回後確認 `originaldata` 真的出現在合併錨點那一格，不能只看 merges 設定對不對。
4. **驗證**：用 `bimteki:get_project_table_templates(template_guid=新guid)` 讀回，逐項核對：列欄數（＝ `N` 欄）、合併、粗體、charwidth、newline、equalCol、各樓層列的 storyGuid（單棟為各層、一般多棟為各棟總計各層、連棟透天為各棟各層＋各棟小計＋全案總計）、總計列的 storyGuid（全案總計）。**連棟透天另外核對**：col 0 棟別欄的垂直合併是否精準涵蓋每棟的樓層數+1（樓層＋小計），棟別文字（Ｘ棟）是否正確；總計列的棟別+層別欄是否合併成一格（colspan 2）且內容在 col 0；機電/地下層檢討列的標籤+內容是否合併成一格（colspan `Dcol`，覆蓋到 B 群最後一欄）且 D 欄數值格保持獨立；以及各處合併相鄰欄位之間的框線是否完整（`rightLine`／`bottomLine`／`topLine` 不要出現整欄 0）。有出入就用 modify 修正後再讀回確認。已知現象：剛建立的樣板 `statedata` 會顯示原始 token 字串，這是尚未評估的正常狀態，放置到圖面後才會解析成實際值，不需處理；核對內容以 `originaldata` 是否含正確 token 為準。
5. 向使用者簡短回報：案型（共用/非共用、單棟/多棟/連棟透天、棟數）、樣板名稱、最終列欄數（連棟透天含棟別欄）、因非共用或 0 值而移除了哪些欄、樓層列對應狀況、機電空間與地下層兩列檢討各自是否顯示及原因（機電面積為 0 而省略／非總量檢討或無地下層面積而省略），並提醒可在 BIMTeki 表格管理器中放置到圖面。若 0 值過濾因 API 未提供而略過，一併說明。

## 儲存格寫法

- **固定文字**：`{"row": r, "col": c, "text": "小　計"}`。標題與標籤中的全形空白（例如「各　層　樓　地　板　面　積」「項　目」「小　計」「總　計」）要照抄，這是排版慣例。
- **純自動文字**：用 segments 帶 token，並在 cell 上加 `storyGuid`（樓層列用該樓層 guid；總計列用全案總計 guid）：
  ```json
  {"row": 4, "col": 1, "storyGuid": "{...樓層guid...}",
   "segments": [{"type": "autotext", "token": "${TJL$F...}"}]}
  ```
- **混合文字與自動文字**（檢討列）：segments 交錯 text 與 autotext，換行用 `\n`：
  ```json
  {"segments": [
    {"type": "text", "value": "允建機電面積："},
    {"type": "autotext", "token": "${...允建機電設備空間計算式...}"},
    {"type": "text", "value": "，\n回計檢討："},
    {"type": "autotext", "token": "${...機電設備檢討式...}"}
  ]}
  ```
- **格式欄位**（可與內容欄位並列於同一 cell 物件）：
  - `textbold`: true/false — 粗體
  - `charwidth`: 0 正常 / 1 **縮減字寬**
  - `newline`: 0 不換行 / 2 **依照中文換行**
  - `alignment`: 1 靠左 / 2 置中
  - `textsize`: 1 大（僅表格大標題）/ 2 一般
  - `rowspan` / `colspan`：合併儲存格
- volumeCheck 類 token（startmanager）不需要 storyGuid；固定文字格也可省略 storyGuid。

## 注意事項

- 本 skill 會在專案中新建樣板（寫入專案並存檔），屬於可逆性低的操作；動手前先讓使用者知道即將建立的樣板名稱與判斷出的案型。若要刪除舊樣板（`manage_project_table_templates` 的 delete）必須先取得使用者明確同意。
- 一次 create 的 cells 數量可能很大（十幾欄 × 20 多列）；請完整組好再一次送出，不要分多次 create 產生多個殘缺樣板。若 create 失敗，修正後重試前先確認沒有留下半成品樣板。
- 欄位是動態的：務必先完成過濾與重新編號，再組 cells／merges；不要沿用固定的 19 欄索引。
- 表格類型維持 `normal`；不要設定 story_guid / room_guid 的樣板層級綁定（樓層脈絡由各儲存格的 storyGuid 決定）。
