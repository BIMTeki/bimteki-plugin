---
name: table
argument-hint: "[清單|面積|法規]"
description: BIMTeki 建照「檢討表格」的清單與入口說明。當使用者說「製作檢討表格 / 產生檢討表 / 這個建照有哪些檢討表可以做 / 檢討表清單 / 哪些表可以自動化 / make review tables」但**沒有點名是哪一張表**時使用本 skill，即使沒有明講「skill」二字。本 skill 不建表、不路由到單張表：只依 references/table-catalog.md 列出本案可做的表，並指到兩個分類 hub——面積與容積類（面積總表、各層容積、地下層容積、屋突、建蔽率、基地概要）用 `table-area`，法規條文類（建照審查表、土管、無障礙）用 `table-code`；自訂面積項目檢討與土管綠化面積檢討用 `custom-area-review`，綠建築基準檢討用 `green-all`。使用者已點名要哪張表或哪一類時，直接用該表的 skill 或分類 hub，不必經過本 skill。三份共用參考（spoke-conventions／mcp-compat／table-catalog）放在本 skill 的 references 供各 spoke 引用。
---

# BIMTeki 檢討表格清單（入口）

一份建照圖說裡有十幾種檢討表。本 skill 只回答「有哪些表、哪些能用 BIMTeki 自動化、該找哪個 skill」，實際建表一律交給分類 hub 與各表專屬 skill；本 skill 不寫任何 cells。

> 只是想知道有哪些表時不需連線；要建表時由分類 hub 做前置檢查。

## 兩個分類 hub

| 類型 | hub | 收哪些表 | 共同特徵 |
|---|---|---|---|
| 面積與容積檢討 | `table-area` | 各層樓地板面積總表、各層容積檢討、地下層容積檢討、屋突面積檢討、建蔽率檢討、基地概要表 | 數值表，值全綁 autotext 由 BIMTeki 即時計算；多數 story 相依、要帶 storyGuid；案型分支多 |
| 法規條文檢討 | `table-code` | 建照審查表（第 18～27 項）、土管檢討表、無障礙建築檢討表 | 左欄條文逐字照抄、右欄依本案填寫；重點在條文來源、樣板句與佔位符 |

不經 hub 的：

- **土管綠化面積檢討**（綠化率、喬木株數）與**自訂面積項目檢討**（宜居建築等使用者自訂檢討方式）→ `custom-area-review`。
- **綠建築基準檢討**（技則第十七章：基地綠化固碳、保水、節能、綠建材）→ `green-all`。
- **各層平面圖法規檢討表**（畫在各層平面圖上）→ `table-floor-plan-code`，獨立 skill、**開發中未對外發佈**；使用者端找不到時直接說明尚未提供，不要自己建。

## 流程

1. 帶參數 `清單`（或沒帶參數）：依 `references/table-catalog.md` 列出本案可做的表，按上面兩類分組，並標明各表的 skill；請使用者挑要做哪一張或哪一類。不要一次全建、不要在本 skill 內建表。
2. 帶參數 `面積` → 交給 `table-area`；`法規` → 交給 `table-code`。使用者直接說出表名（例「做建蔽率檢討」）就交給對應分類 hub 或該表 skill，不要再列清單。
3. 清單以外、尚無專屬 skill 的表：直接說明目前沒有對應的 skill，本 skill 不代建、不要自己組表。逐段面積計算式表（`尺寸×尺寸=面積` 一列一段）與純圖類（如無障礙檢討平面圖）不是可自動化的檢討表，不列入清單、不嘗試生成；面積來源可建議用 `bimteki:split_areas_and_return_map`／`get_bimteki_zone_map` 取數據輔助人工填表。

## 共用參考的家

各 spoke 與兩個分類 hub 共用的規範放在本 skill 的 `references/`，其他 skill 以 `references/…` 相對路徑引用（發佈時會複製一份到各 spoke 自己的 `references/`）；改共通行為只改這一份：

- `references/spoke-conventions.md`：前置檢查、唯讀工具、autotext 原則、佔位符與樣板句、儲存格格式、建表共通流程、寫入底線。
- `references/mcp-compat.md`：所有 skill 的需求版本單一來源（MCP／外掛／圖庫）。
- `references/table-catalog.md`：檢討表路由總表、autotext 分類速查。
