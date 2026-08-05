---
name: table
argument-hint: "[permit|coverage|area|volume|basement|rooftop|landuse|a11y|site|green|list]"
description: BIMTeki「製作檢討表格」的單一入口與總調度（hub）。凡是要做建照圖說裡的任何一張檢討表都從這裡進來——面積總表、各層容積、地下層容積、屋突、建照審查、土管、無障礙、基地概要、建蔽率、綠化。當使用者想要「製作檢討表格 / 產生檢討表 / 做面積表 / 做容積檢討 / 做建照審查表 / 做土管表 / 做無障礙檢討 / 做建蔽率檢討 / 做綠化檢討 / 做基地概要 / 做屋突檢討 / 這個建照有哪些檢討表可以做 / make review tables」時務必使用本 skill，即使沒有明講「skill」二字。可帶關鍵字直接指定要哪張表，例如 `/bimteki:table permit`（建照審查表）、`coverage`（建蔽率）、`area`（面積總表）——完整對照見下方「參數對照」。本 skill 不直接建表、不畫圖、不查法規，只負責確認連線與案型、判斷該表能否自動化、路由到各表專屬 skill；實際建表一律交給專屬 skill。逐段面積計算式表與純圖類不在範圍內。
---

# BIMTeki 製作檢討表格（總調度 hub）

這是「製作檢討表格」的入口 skill。一份建照圖說（本範例為 A0-01～A0-14）裡有十幾種檢討表，能否用 BIMTeki 的表格樣板工具製作、以及該交給哪個 skill，差異很大。本 skill 採 **hub-and-spoke**：自己只做「分類與路由」，實際建表交給各表專屬 skill，避免同一張表出現兩套不一致的實作。

核心原則（各 spoke skill 共用）：表格數值一律用**自動文字（autotext）**綁定、由 BIMTeki 即時計算，不寫死；BIMTeki 無法得知的外部資訊（函號、日期、核准圖號）一律留佔位符，不臆測。

> 需求前提：實際建表需連上使用者本機的 Archicad + BIMTeki Studio。若只是想「知道有哪些表、哪些可自動化」，可直接依 `references/table-catalog.md` 回答，不需連線。

## 流程

1. **前置檢查**：呼叫 `bimteki:check_connection`（純諮詢可略過）。要建表時再 `bimteki:get_project_status`（唯讀、成本低）確認可讀專案、並看 `finalized`（已定案）與 `project_file.hasFile`（false＝專案只在記憶體中、變更無法落地，請使用者先另存新檔）；回報未開啟專案則詢問路徑後 `bimteki:open_bimteki_project`。呼叫 `bimteki:get_project_core_snapshot` 取案型（以 `building.case_type` 為準）供分類。
2. **釐清要做哪張表**：**呼叫本 skill 時若帶了參數（如 `/bimteki:table permit`），先查下方「參數對照」直接認定要做哪張表，不要再問一次、也不要列清單**；參數可以是關鍵字、中文表名或其簡稱，比對不到才回頭問。沒帶參數且只說「製作檢討表格」時，先用 `references/table-catalog.md` 摘要本案可做的檢討表清單（分兩類：A 有專屬 skill／B 可綁 autotext 尚無 skill），請使用者勾選。不要一次全建。若使用者要的是逐段面積計算式表或純圖類（非本 skill 範圍），直接說明本 skill 不做這類，不要嘗試生成。
3. **分類並路由**（見下）。
4. **回報**：說明各表交給了哪個 skill（A 類）或如何自建（B 類）。

## 參數對照（`/bimteki:table <關鍵字>`）

帶參數時直接對到下表的 skill，跳過詢問。關鍵字大小寫不拘，中文表名／簡稱同樣有效。

| 關鍵字 | 中文／別名 | 檢討表 | 交給 |
|---|---|---|---|
| `area` | 面積總表、樓地板面積 | 各層樓地板面積總表 | `bimteki-area-summary-table` |
| `volume` | 容積、各層容積 | 各層容積檢討表（每地上層一張） | `bimteki-per-floor-volume-review-table` |
| `basement` | 地下層、地下室 | 地下層容積檢討表 | `bimteki-basement-volume-review-table` |
| `rooftop` | 屋突 | 屋突面積檢討表 | `bimteki-rooftop-area-review-table` |
| `permit` | 建照審查、審查表 | 建照審查表第18~27項 | `bimteki-permit-review-table` |
| `landuse` | 土管、土地使用分區 | 土管檢討表 | `bimteki-landuse-review-table` |
| `a11y` | 無障礙 | 無障礙建築檢討表 | `bimteki-accessibility-review-table` |
| `site` | 基地概要、基地資訊 | 基地概要表 | `bimteki-site-overview-table` |
| `coverage` | 建蔽率、建築面積檢討 | 建蔽率檢討表 | `bimteki-coverage-review-table` |
| `green` | 綠化、綠覆 | 綠化面積檢討表 | `bimteki-green-area-review-table` |

`list` / `清單`＝只列出本案可做的檢討表，不建表。參數比對不到任何一列時，不要猜——列出上表請使用者指定。

## 分類與路由（以 references/table-catalog.md 為準）

### A. 有專屬 skill → 路由過去（本 skill 不重做）

| 檢討表 | 圖號 | 路由到 |
|---|---|---|
| 各層樓地板面積總表 (A)(B)(C)(D) | A0-01 | `bimteki-area-summary-table` |
| 各層容積檢討表（每一地上樓層一張） | A0-12~14 | `bimteki-per-floor-volume-review-table` |
| 地下層容積檢討表（地下層總計容積檢討，含停車空間） | A0-11 | `bimteki-basement-volume-review-table` |
| 屋突面積檢討表 | A0-12~14 | `bimteki-rooftop-area-review-table` |
| 建造執照及雜項執照規定項目審查表（第18~27項） | A0-01 | `bimteki-permit-review-table` |
| 土地使用分區管制要點檢討（土管檢討表） | A0-02 | `bimteki-landuse-review-table`（需使用者提供土管 PDF；三欄式） |
| 建築技術規則設計施工篇第十章 無障礙建築 | A0-06 | `bimteki-accessibility-review-table` |
| 基地概要表（基地資訊/建蔽容積規定值vs設計小表） | A0-01 | `bimteki-site-overview-table` |
| 建蔽率檢討表（表格標題「建築面積檢討」：基地面積→扣除項→使用面積→設計建築面積→建蔽率檢討） | A0-03 | `bimteki-coverage-review-table` |
| 綠化面積檢討表（實設空地/法定空地→綠化面積→綠化困難→應綠化→喬木數量；**都計內/有土管才須做**） | A0-05 | `bimteki-green-area-review-table`（先判都計內外，非都計免檢討；規定值依土管） |

路由方式：告知使用者「這張表由 ⟪skill 名⟫ 負責」，交給該 skill 接手。土管表特別注意：`landuse-review-table` 會**讀使用者上傳的土管文件**逐條萃取條文，若使用者沒附文件，先請他提供再路由。

### B. autotext 可綁、尚無專屬 skill → 依 catalog 分類自行建表

彙整結果類表（多為 autotext 可綁），本 skill 生態尚未各自成 skill：畸零地檢討小表(A0-01)、宜居建築設施設置及回饋辦法＋自治條例第50條(A0-08)。若使用者要做，依 `references/table-catalog.md` 標註的 autotext 分類比對 catalog 建表，流程與其他兩欄/多欄表相同（差別只在欄位與列的組法），沒把握的欄位退回佔位符。**這些未來也建議各自拆成獨立 skill**（與現有生態一致），需要時再新增。

> 註：宜居建築設施設置及回饋辦法＋自治條例第50條檢討表（A0-08）原有專屬 skill，現已移除，改歸 B 類。此表屬「法規逐條檢討」（兩欄式，同無障礙／建照審查表形式），可綁 autotext 者（基地面積、容積樓地板面積、法定/設計容積率、樓層數）優先綁，其餘填標準樣板句、外部函號留佔位符；需要時可比照兩欄式法規檢討表流程建表或重建 skill。

### 不在範圍內：逐段面積計算式表、純圖類

「面積計算式」類（每列一段 `尺寸 × 尺寸 = 面積`，來自實際量測的多邊形邊段）與純圖類（如各層無障礙檢討平面圖）**不是可自動化的檢討表，本 skill 不做、也不列入清單**。若使用者要這類，直接說明本 skill 不處理；面積來源可另建議用容積區域繪製 skill（`bimteki-volume-zones-v2`）或 `bimteki:split_areas_and_return_map` / `get_bimteki_zone_map` 取數據輔助人工填表。不要假裝能一鍵生成、不要捏造計算式列。

## 各 spoke 共用的 MCP 眉角（最新工具版本）

這幾點在每個建表 skill 裡都成立，路由前可先提醒：

- **`create_project_table_template` 已能一步建完整表**（v0.7.1 起支援 `merges` / `equal_col` /
  `right_line` / `bottom_line` / `left_line` / `top_line`）。合併只能用 `merges` 參數——寫在 cell 上的
  `rowspan`/`colspan` 建立時會被忽略。`modify_project_table_template` 現在只剩樣板名、`column_widths`、
  `table_type`／`story_guid` 等樣板層級屬性要補。
- **求值要挑對工具**：`evaluate_story_autotext_values` **只涵蓋 storyArea 分類**；綠化／停車／建蔽／
  容積檢討／屋突／通風採光／基地概要等其他分類，一律用通用版
  `evaluate_autotext_values(category=...)`。用錯不會報錯、只會回空，很容易被誤判成 0。
- **陣列自動文字無法求值**（要放到圖紙才展開）；地下層停車清單的實際數字改讀 `get_project_parking_info`。
- **modify 在團隊協作專案可能整批失敗**：有表格被其他使用者保留時回傳 `lockedTables` 且不做任何修改，
  要把清單轉告使用者請對方釋放，不要重試硬闖。
- 專案事實各有專屬唯讀工具：`get_project_stories`（樓層骨架／夾層屋突旗標／戶數樓高用途）、
  `get_project_parking_info`、`get_project_green_info`、`get_project_custom_params`、`get_project_status`。

## 注意事項

- 本 skill 不寫任何建表 cells——建表細節屬各 spoke skill。若在本 skill 內重做，會造成兩套不一致的實作。
- 新建樣板會寫入專案並存檔（由 spoke skill 執行），屬可逆性低操作；動手前先讓使用者知道樣板名稱。刪除舊樣板須先取得使用者明確同意。
- 「非…故免檢討」類樣板句是常見預設，BIMTeki 無法驗證是否屬實；由 spoke skill 於回報時提醒使用者確認。
