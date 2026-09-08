---
name: table-area
argument-hint: "[面積總表|容積|地下|屋突|建蔽|基地|清單]"
description: BIMTeki「面積與容積檢討表」的分類入口與調度（hub）。當使用者想要「做面積表 / 做面積總表 / 做容積檢討 / 做地下層容積檢討 / 做屋突檢討 / 做建蔽率檢討 / 做基地概要 / 這些面積容積的表可以做哪些 / area and volume review tables」時務必使用本 skill，即使沒有明講「skill」二字。可帶關鍵字直接指定要哪張表，例如 `/bimteki:table-area 建蔽`、`面積總表`、`容積`；英文 `coverage`／`area`／`volume`／`basement`／`rooftop`／`site` 同樣接受。**先決條件：使用者必須先在 Archicad 把容積區域與建蔽（建築面積）區域繪製完成並匯入 BIMTeki**，表格的值全靠這些區域計算；本 skill 會先檢查區域是否存在，沒有就停手請使用者先繪製匯入，不建表。本 skill 不直接建表，只確認連線、案型與區域是否就緒、判斷該表能否自動化，路由到各表專屬 skill（`table-area-summary`／`table-area-per-floor-volume`／`table-area-basement-volume`／`table-area-rooftop`／`table-area-coverage`／`table-area-site-overview`）。法規條文類（建照審查表、土管、無障礙）是另一個 hub `table-code`，不在本 skill 範圍。
---

# BIMTeki 面積與容積檢討表（分類 hub）

本 hub 收的表都是**數值表**：值來自 BIMTeki 區域與專案資訊、全綁 autotext 即時計算，多數與樓層相依。本 skill 採 hub-and-spoke：自己只做分類與路由，實際建表交給各表專屬 skill，避免同一張表出現兩套實作。

核心原則（各 spoke 共用）：數值一律用 autotext 綁定、不寫死；BIMTeki 無法得知的外部資訊留佔位符，不臆測。

> 需求前提：實際建表需連上使用者本機的 Archicad + BIMTeki Studio。

## 先決條件：容積區域與建蔽區域已繪製並匯入 BIMTeki

本 hub 的六張表沒有任何值是手填的，全部由 BIMTeki 匯入的區域算出來：

| 表 | 依賴的區域 |
|---|---|
| 各層樓地板面積總表、各層容積檢討、地下層容積檢討、屋突面積檢討 | **容積區域**（各層都要畫、都要匯入 BIMTeki 容積工具；地下層與屋突層也算在內） |
| 建蔽率檢討、基地概要表 | **建蔽區域**（請照空間名稱「建築面積」及其扣除項，匯入建築面積分頁）；基地概要另會引用容積值 |

所以使用者要先在 Archicad 自己畫好這些區域，並從 BIMTeki 面板**匯入**。檢查方式與缺席時的處理是共用規範（`../table/references/spoke-conventions.md` 第 1 節第 4 步），本 hub 與六支 spoke 都做同一套：本 hub 與各 spoke **不代為繪製、不呼叫任何建立區域的工具**，區域缺席時不建表，請使用者補齊後再回來。

## 流程

1. **前置檢查**：`bimteki:check_connection`（多開時先選 instance）。**回傳最後一行「版本：」要看過**（沒有這行代表 MCP 早於 0.8.0，照常往下走、不要擋）；需求版本與版本不足時的處理見 `../table/references/mcp-compat.md`，真的不夠就停手請使用者重跑安裝檔，不要改用舊流程默默建表。再 `bimteki:get_project_status`（唯讀）確認可讀專案、看 `finalized`（已定案）與 `project_file.hasFile`（false＝專案只在記憶體中、變更無法落地，請先另存新檔）；未開啟專案則詢問路徑後 `bimteki:open_bimteki_project`。最後 `bimteki:get_project_core_snapshot` 取**案型**（以 `building.case_type` 為準）——本 hub 的表幾乎都依案型分支（單棟／一般多棟／連棟透天）。
   **接著檢查先決條件**（共用規範第 1 節第 4 步）：`bimteki:get_bimteki_zone_map` 看要做的表所依賴的區域是否存在，是 0 就停手請使用者先繪製匯入，不要路由、不要建表。
2. **釐清要做哪張表**：帶參數時先查下方「參數對照」直接認定，不要再問、不要列清單；沒帶參數就列出本 hub 的表請使用者勾選，不要一次全建。
3. **路由**：告知使用者「這張表由 ⟪skill 名⟫ 負責」，交給該 skill 接手。
4. **回報**：說明各表交給了哪個 skill。

## 參數對照（`/bimteki:table-area <關鍵字>`）

| 關鍵字 | 也接受 | 檢討表 | 交給 |
|---|---|---|---|
| `面積總表` | `area`、面積、樓地板面積、各層樓地板面積 | 各層樓地板面積總表 (A)(B)(C)(D) | `table-area-summary` |
| `容積` | `volume`、各層容積、地上層容積 | 各層容積檢討表（每地上層一張） | `table-area-per-floor-volume` |
| `地下` | `basement`、地下層、地下室 | 地下層容積檢討表（地下層總計容積檢討，含停車空間） | `table-area-basement-volume` |
| `屋突` | `rooftop` | 屋突面積檢討表 | `table-area-rooftop` |
| `建蔽` | `coverage`、建蔽率、建築面積檢討 | 建蔽率檢討表（表格標題「建築面積檢討」） | `table-area-coverage` |
| `基地` | `site`、基地概要、基地資訊 | 基地概要表（基地資訊／建蔽容積規定值 vs 設計小表） | `table-area-site-overview` |
| `清單` | `list` | 只列出本 hub 可做的表，不建表 | （本 skill 自己回答） |

注意「`容積`」是**地上層**的各層容積檢討，地下層要用「`地下`」——兩者是不同的表。參數比對不到任何一列時不要猜，列出上表請使用者指定；使用者要的是法規條文類（審查表、土管、無障礙）就指到 `table-code`。

## 面積類 spoke 共用的眉角

前置檢查、唯讀工具、autotext 原則、儲存格格式、建表共通流程與寫入底線，統一收在 `../table/references/spoke-conventions.md`（各 spoke 都指回那一份）。路由前最值得先提醒的幾點，都是本類表特有的坑：

- **案型決定版面**：面積總表、各層容積依案型有不同欄位與樓層列（單棟／一般多棟／連棟透天），多棟另有「各棟總計」虛擬棟別；先取案型再路由。
- **story 相依 token 要帶 storyGuid**：`storyArea`、`roofArea` 等（`needGUID: true`）在儲存格上帶該層 guid，總計列帶全案總計 guid；樓層骨架用 `get_project_stories` 的 `blocks[].stories`，不是 `floors`。
- **求值要挑對工具**：`evaluate_story_autotext_values` 只涵蓋 `storyArea`；`coverage`／`volumeCheck`／`roofArea`／`customAreaReview` 等一律用 `evaluate_autotext_values(category=...)`，用錯不報錯、只回空。陣列自動文字無法求值，地下層停車的數字改讀 `get_project_parking_info`。
- **判 0 容差 `abs(value) < 0.005`**；求值失敗時不要臆測、不要用區域圖資硬湊，保留所有列並在回報說明。
- **`create_project_table_template` 一步建完整表**（`merges`／`equal_col`／框線）；合併只能用 `merges`，每格明確給 `newline`。
- **團隊協作的 modify 可能整批失敗**：回傳 `lockedTables` 時不做任何修改，把清單轉告使用者請對方釋放，不要重試硬闖。

## 注意事項

- 本 skill 不寫任何建表 cells；沒有 spoke 的表就不做，直接說明目前沒有對應的 skill。逐段面積計算式表（`尺寸×尺寸=面積`）與純圖類不在範圍。
- 新建樣板會寫入專案並存檔（由 spoke 執行），屬可逆性低操作；動手前先讓使用者知道樣板名稱。刪除舊樣板須先取得使用者明確同意。
