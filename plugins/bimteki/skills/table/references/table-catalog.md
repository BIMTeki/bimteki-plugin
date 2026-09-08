# 建照圖說檢討表清單與 BIMTeki 可行性分類（路由對照表）

本檔對照一份標準建照圖說，列出**已有專屬 skill** 的每張檢討表、資料來源、以及**該路由到哪個 skill**。逐段量測的面積計算式表（`尺寸×尺寸=面積`）、純圖類非表格項目，以及尚無專屬 skill 的表都不列；hub 對後者一律說明「目前沒有對應的 skill」、不代建。

> 表的「種類」與路由邏輯通用於各案；實際建表一律以目前開啟專案的 `get_project_autotext_catalog` 回傳為準。

## 路由總表

路由欄的 skill 分屬兩個分類 hub：**面積與容積類 → `table-area`**（面積總表、各層容積、地下層、屋突、建蔽率、基地概要，綠化指到 `custom-area-review`）；**法規條文類 → `table-code`**（建照審查、土管、無障礙）。`table-floor-plan-code` 獨立、不經 hub。`table` 本身只列清單與指路。

| 檢討表 | 資料來源 | 路由 |
|---|---|---|
| 各層樓地板面積總表（(A)(B)(C)(D)） | 各層面積+容積回計 | → `table-area-summary` |
| 建造執照及雜項執照規定項目審查表（第18~27項） | 法規+專案事實 | → `table-code-permit` |
| 土地使用分區管制要點檢討（土管檢討表，三欄式） | 使用者上傳土管PDF+專案事實 | → `table-code-landuse`（需附土管文件） |
| 建築技術規則設計施工篇第十章 無障礙建築 | 法規+專案事實 | → `table-code-accessibility` |
| 基地資訊表／建蔽容積規定值vs設計小表（基地概要表） | siteOverview/buildingOverview/coverage/volumeCheck | → `table-area-site-overview` |
| 地下層容積檢討表（地下層總計容積檢討；樓層/車位數/停車樓地板面積；防空避難室；可扣容積；地下室容積檢討） | volumeCheck/parking/arrayField | → `table-area-basement-volume` |
| 各層容積檢討表（每地上層一張；當層樓地板面積·10%·15%·陽台/梯廳回計·機電·容積樓地板面積） | storyArea/volumeCheck | → `table-area-per-floor-volume` |
| 屋突面積檢討表（屋突面積/允建屋突面積/檢討） | roofArea/storyArea（story 相依） | → `table-area-rooftop` |
| 建蔽率檢討表（表格標題「建築面積檢討」：基地面積→保留地/道路退縮地/鄰房侵占/騎樓/騎樓地扣除→使用面積→設計建築面積→建蔽率檢討） | coverage | → `table-area-coverage` |
| 綠化面積檢討表（實設空地/法定空地→綠化面積→綠化困難→應綠化→喬木數量；**限都計內/有土管或特殊條例才須做，非都計免檢討**） | customAreaReview（項目「綠化面積檢討」的組合）＋customParam（規定值）＋coverage／siteOverview（基準空地）＋`{=}`/`{?}` | → `custom-area-review`（土管綠化案例：先判都計內外、規定值依土管；不經 hub） |
| 各層平面圖法規檢討表（兩欄式：`○○檢討：#NN`＋條文原文＋粗體檢討結論；每層各一張，標準層可跨層共用；依樓層角色增減條列） | 法規＋專案事實＋storyArea | → `table-floor-plan-code`（**開發中、未對外發佈**；獨立 skill，不經 hub） |

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
- `customAreaReview`（自訂面積項目檢討）：散裝區域面積、區域組合的合計與計算式 token；綠化面積也在這裡（項目「綠化面積檢討」的組合「實設綠化面積」「無法綠化面積」）。→ `custom-area-review`。
- `customParam`（使用者自訂義參數）：欄位鍵 `CustomParam.{項目名}`；綠化規定值（綠化比率／喬木檢討基準／實設喬木數量／檢討基數）存在分類「綠化面積檢討」。
- 停車類：以 catalog 實際回傳的 display 為準比對（版本命名可能不同）。

Token 是專案特定的，**絕不憑記憶或跨專案硬編**；一律 catalog 比對後取用。

## 現有 spoke skill 一覽

| 檢討表 | skill 名 | 備註 |
|---|---|---|
| 各層樓地板面積總表 | `table-area-summary` | 依案型動態欄位 |
| 各層容積檢討表（每地上層一張） | `table-area-per-floor-volume` | 三欄式，storyArea 算式綁定；夾層/工廠類/各棟總計等變體 |
| 地下層容積檢討表 | `table-area-basement-volume` | 全案一張，含地下層停車陣列 autotext |
| 屋突面積檢討表 | `table-area-rooftop` | 兩欄固定四列，roofArea/storyArea story 相依 |
| 建照審查表（第18~27項） | `table-code-permit` | 固定10項兩欄 |
| 土管檢討表 | `table-code-landuse` | 三欄式，讀使用者土管PDF |
| 無障礙建築檢討表 | `table-code-accessibility` | 兩欄，第167條系列 |
| 基地概要表（基地資訊/建蔽容積規定值vs設計小表） | `table-area-site-overview` | 兩欄，含7項法規檢討與算式列 |
| 建蔽率檢討表（建築面積檢討） | `table-area-coverage` | 兩欄，coverage 算式綁定；扣除列（保留地/退縮地/鄰房侵占/騎樓/騎樓地）依面積>0 條件顯示，騎樓地另需扣除設定 |
| 各層平面圖法規檢討表（畫在各層平面圖上） | `table-floor-plan-code` | **開發中（不公開）**；兩欄拆列（條文列＋粗體檢討列、條號遞增），依樓層角色與規模增減條列；#33 樓梯尺寸可另建 stairInfo 子表 |
