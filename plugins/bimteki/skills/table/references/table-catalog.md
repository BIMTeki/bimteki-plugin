# 建照圖說檢討表清單與 BIMTeki 可行性分類（路由對照表）

本檔對照一份標準建照圖說的 A0 系列圖面，列出**可自動化**的每張檢討表、資料來源、以及**該路由到哪個專屬 skill**。本 skill 只處理可自動化（autotext 可綁）的檢討表；逐段量測的面積計算式表（`尺寸×尺寸=面積`）、純圖類非表格項目不在範圍內，本表不再列出。分類代碼：

- **A｜已有專屬 skill**：路由過去，本 hub 不重做。
- **B｜autotext 可綁、尚無專屬 skill**：屬彙整結果表，可做；依 catalog 分類自行比對建表，沒把握退佔位符。建議未來各自拆成獨立 skill。

> 圖號以本範例專案（台中市南屯區永新段，七層辦公室暨住宅大樓）為準；不同案子圖號會不同，但表的「種類」與路由邏輯通用。實際建表一律以目前開啟專案的 `get_project_autotext_catalog` 回傳為準。

## 分類與路由總表

| 圖號 | 檢討表 | 資料來源 | 分類 | 路由 / autotext 分類 |
|---|---|---|---|---|
| A0-01 | 各層樓地板面積總表（(A)(B)(C)(D)） | 各層面積+容積回計 | **A** | → `bimteki-area-summary-table` |
| A0-01 | 建造執照及雜項執照規定項目審查表（第18~27項） | 法規+專案事實 | **A** | → `bimteki-permit-review-table` |
| A0-02 | 土地使用分區管制要點檢討（土管檢討表，三欄式） | 使用者上傳土管PDF+專案事實 | **A** | → `bimteki-landuse-review-table`（需附土管文件） |
| A0-06 | 建築技術規則設計施工篇第十章 無障礙建築 | 法規+專案事實 | **A** | → `bimteki-accessibility-review-table` |
| A0-01 | 基地資訊表／建蔽容積規定值vs設計小表（基地概要表） | siteOverview/buildingOverview/coverage/volumeCheck | **A** | → `bimteki-site-overview-table` |
| A0-11 | 地下層容積檢討表（地下層總計容積檢討；樓層/車位數/停車樓地板面積；防空避難室；可扣容積；地下室容積檢討） | volumeCheck/parking/arrayField | **A** | → `bimteki-basement-volume-review-table` |
| A0-12/13/14 | 各層容積檢討表（每地上層一張；當層樓地板面積·10%·15%·陽台/梯廳回計·機電·容積樓地板面積） | storyArea/volumeCheck | **A** | → `bimteki-per-floor-volume-review-table` |
| A0-12/13/14 | 屋突面積檢討表（屋突面積/允建屋突面積/檢討） | roofArea/storyArea（story 相依） | **A** | → `bimteki-rooftop-area-review-table` |
| A0-08 | 鼓勵宜居建築設施設置及回饋辦法（第1~22條） | 法規+專案事實 | **B**（無專屬 skill） | 原 `bimteki-livable-building-review-table` 已移除；兩欄式法規檢討，可綁 volumeCheck/siteOverview |
| A0-08 | 都市計畫法台中市施行自治條例 第50條 | 法規+專案事實 | **B**（無專屬 skill） | 同上，可與宜居辦法併出一張 |
| A0-03 | 建蔽率檢討表（表格標題「建築面積檢討」：基地面積→保留地/道路退縮地/鄰房侵占/騎樓/騎樓地扣除→使用面積→設計建築面積→建蔽率檢討） | coverage | **A** | → `bimteki-coverage-review-table` |
| A0-01 | 畸零地檢討小表（寬度/深度 法定vs基地） | 基地尺寸 | **B**（部分佔位） | autotext: `siteOverview`；面前道路寬多半無→佔位 |
| A0-05 | 綠化面積檢討表（實設空地/法定空地→綠化面積→綠化困難→應綠化→喬木數量；**限都計內/有土管或特殊條例才須做，非都計免檢討**） | green 類 | **A** | → `bimteki-green-area-review-table`（先判都計內外；規定值依土管） |
| 依案而定 | 自訂面積項目檢討表（地方特別法規等自訂面積比例檢討，例：宜居建築垂直綠化；建一個總檢討項目→掛散裝區域／區域組合→組比例） | customAreaReview | **A** | → `bimteki-custom-area-review-table`（需 MCP ≥ 0.12.0 與模組授權） |

## 判斷「能不能綁 autotext」的通則

1. **結果是「一個由模型算出的量」**（面積、比率、樓地板面積、車位數、回計值）→ 幾乎都有 autotext，優先綁。以 catalog 回傳的 `display` 名稱比對取 `token`。
2. **結果是「逐項量測的計算式」**（`a×b=c` 一列一段）→ 無現成 autotext，**不在本 skill 範圍**，不要嘗試以表格樣板生成。
3. **結果是「外部文件引用」**（函號、核准日期、都計案名、核准圖號、公告地價）→ BIMTeki 無法得知，留佔位符：文號 `◯◯◯字第◯◯◯◯◯號`、日期 `○○○年○○月○○日`、圖號 `A0-○`。
4. **樓層相關欄位**（各層容積檢討、屋突面積檢討等 story 相依表）→ autotext 需在儲存格帶 `storyGuid`（該樓層 guid；總計列帶全案總計 guid）。專案層級欄位不需 storyGuid。

## 各 autotext 分類速查（category 參數）

- `siteOverview`：基地地號、使用分區、基地面積、基地尺寸/寬深。
- `buildingOverview`：建築物用途/組別、層數、戶數、面前道路。
- `coverage`：法定/設計建蔽率、建築面積、法定空地。
- `volumeCheck`：法定/設計容積率、允建/設計容積樓地板面積、機電回計式、停車/地下室容積檢討式。
- `storyArea`（targetTypeName: story，需 storyGuid）：樓層名稱、當層樓地板面積、各空間面積、用途。
- `green`（綠化類）：實設空地/法定空地、設計綠化面積、無法綠化面積、應設綠化面積算式、綠化面積檢討式、喬木檢討式。→ `bimteki-green-area-review-table`。
- 停車類：以 catalog 實際回傳的 display 為準比對（版本命名可能不同）。
- `customAreaReview`：自訂面積項目檢討的散裝區域面積與區域組合合計。**不需掃 catalog**——token 由專屬工具 `get_project_custom_area_review` 的 `zones[].token`／`groups[].token` 直接取得（同名區域 catalog 分不出來，該工具以 GUID 分）。

Token 是專案特定的，**絕不憑記憶或跨專案硬編**；一律 catalog 比對後取用。

## 現有 spoke skill 一覽

| 檢討表 | skill 名 | 備註 |
|---|---|---|
| 各層樓地板面積總表 | `bimteki-area-summary-table` | 依案型動態欄位 |
| 各層容積檢討表（每地上層一張） | `bimteki-per-floor-volume-review-table` | 三欄式，storyArea 算式綁定；夾層/工廠類/各棟總計等變體 |
| 地下層容積檢討表 | `bimteki-basement-volume-review-table` | 全案一張，含地下層停車陣列 autotext |
| 屋突面積檢討表 | `bimteki-rooftop-area-review-table` | 兩欄固定四列，roofArea/storyArea story 相依 |
| 建照審查表（第18~27項） | `bimteki-permit-review-table` | 固定10項兩欄 |
| 土管檢討表 | `bimteki-landuse-review-table` | 三欄式，讀使用者土管PDF |
| 無障礙建築檢討表 | `bimteki-accessibility-review-table` | 兩欄，第167條系列 |
| 基地概要表（基地資訊/建蔽容積規定值vs設計小表） | `bimteki-site-overview-table` | 兩欄，含7項法規檢討與算式列 |
| 建蔽率檢討表（建築面積檢討） | `bimteki-coverage-review-table` | 兩欄，coverage 算式綁定；扣除列（保留地/退縮地/鄰房侵占/騎樓/騎樓地）依面積>0 條件顯示，騎樓地另需扣除設定 |
| 綠化面積檢討表 | `bimteki-green-area-review-table` | 兩欄，green 算式綁定；**限都計內/有土管才須做**，規定值（比率/喬木密度）依本案土管；綠化困難列依面積>0 條件顯示 |
| 自訂面積項目檢討表 | `bimteki-custom-area-review-table` | 依使用者檢討方式動態組表；建**一個**總檢討項目→掛散裝區域／區域組合（多顆用組合取合計 token，勿寫 `{=a+b+c}`）→組比例；需 MCP ≥ 0.12.0（區域組合）與「自訂面積項目檢討」模組授權 |
| 宜居建築設施＋自治條例第50條 | 已移除（原 `bimteki-livable-building-review-table`） | 兩欄式法規檢討，需要時可重建 skill |
