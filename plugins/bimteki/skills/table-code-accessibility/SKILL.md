---
name: table-code-accessibility
description: 在 BIMTeki 專案中生成「建築技術規則設計施工篇第十章 無障礙建築」檢討表（TableTemplate 表格樣板）。當使用者說「做無障礙檢討表 / 無障礙建築檢討 / 產生無障礙設施檢討表 / accessibility review table」，或由 `table-code` skill 帶 `a11y` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。兩欄式，左欄為第167條及第167-1～167-7條逐字照抄，右欄依本案填寫：能綁 autotext 者優先綁、無對應者填標準樣板句、外部引用留佔位符。逐條內容與 MCP 呼叫順序見本文。建照審查表、土管檢討表另有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 無障礙建築檢討表生成

在目前開啟的 BIMTeki 專案中，建立一份兩欄式「建築技術規則設計施工篇第十章 無障礙建築」檢討表。左欄為固定條文（第167條系列，逐字照抄、不改字），右欄「檢討」依本案填寫。結構與 `table-code-permit` 相同，差別只在條文清單與檢討組法。

右欄組法優先序（本 skill 核心）：
1. **能綁 autotext 就綁** —— 讓 BIMTeki 即時計算，不寫死數字。
2. **無對應 autotext → 標準樣板句** —— 依本案事實選「帶入實際值」或「本案未設…故不適用」。
3. **外部引用 → 佔位符** —— 絕不臆測。

各條的固定條文、需要的資料、autotext 比對關鍵字、樣板句，**以 `references/items.md` 為準**；本檔描述流程。

> 需求前提：需連上使用者本機的 Archicad + BIMTeki Studio。

## 前置檢查

標準順序與細節見 `../table/references/spoke-conventions.md` 第 1 節，摘要：

1. `bimteki:check_connection`（多開時先選 instance）。**版本關卡**：回傳最後一行「版本：」要看過——沒有這行代表 MCP 早於 0.8.0，照常往下走；需求版本與不足時的處理見 `../table/references/mcp-compat.md`，版本不夠就停手請使用者重跑安裝檔，不要改用舊流程默默建表。
2. `bimteki:get_project_status`：`finalized`／`project_file.hasFile`／`has_unsaved_changes`；未開啟專案就問路徑後 `bimteki:open_bimteki_project` 再重試。
3. **專案資料是否填寫齊全**（共用規範第 1 節第 5 步）：讀 `get_project_core_snapshot`（用途組別、層數、戶數、建築高度）與 `get_project_stories`（各層用途），缺的列出來問使用者：先回填（`project-info-fill`）／照現況建表留佔位符／取消；沒答案不建表。
4. 動手前告知即將建立的樣板名稱（預設「無障礙建築檢討表」）與判斷結果，這是寫入專案並存檔的操作；使用者開著表格編輯器等模態視窗時請他先關掉。

## 蒐集專案資訊

呼叫 `bimteki:get_project_core_snapshot`，至少關注：建築物用途/組別（H-2 集合住宅、G-2 辦公室等）、樓層數、是否住宅使用。讀不到就退樣板句或佔位符。

**車位數另用 `bimteki:get_project_parking_info`**（唯讀）：`counts.actual_car`（實設汽車位，由停車區域推導）與 `counts.legal_car`（法定汽車位；`value` 為 -1 且 `isSet=false` 代表尚未填寫）。第167-5 條的無障礙停車位檢討要依汽車位總數換算，用這個工具判斷比從 snapshot 猜可靠。**判斷歸判斷，儲存格仍優先綁 autotext**，不要把讀到的數字寫死。

## 取得自動文字目錄並比對

呼叫 `bimteki:get_project_autotext_catalog(category="buildingOverview,volumeCheck")`（停車位數常在 volumeCheck/parking 類）。掃 `display` 名稱，對 `references/items.md`「自動文字對應」列出的 display 比對取 `token`：

- **找到** → 用 autotext segment。
- **找不到** → 退回文字：可帶入的實際值寫成文字，或依項目填樣板句/佔位符。

**Token 是專案特定的，絕不憑記憶或跨專案硬編**；一律 catalog 比對後取用。用途組別、汽車停車位數通常可綁；無障礙應設數若無現成 token，依「總車位數 → 依表換算」以文字帶入。

## 逐條組內容

依 `references/items.md` 組出各列（第167、167-1～167-7）。每列：
- **左欄（col 0）**：固定條文，含「第167條」等前綴，逐字照抄，不改寫。條文文字建議用 `bimteki:search_building_laws_and_orders` 或使用者現有圖說取現行版本核對。
- **右欄（col 1）**：依優先序 autotext > 樣板句 > 佔位符 組 segments；長句 `newline: 2`。

## 建表流程

共通眉角見 `../table/references/spoke-conventions.md` 第 5～6 節；下面只列本表特有的設定。

1. **組 cells**：
   - Row 0：大標題「建築技術規則設計施工篇第十章 無障礙建築」放 col 0，`textbold:true`、`textsize:1`、`alignment:1`、`charwidth:1`；跨欄合併靠步驟 2 的 `merges`。
   - Row 1~N：col 0、col 1 皆 `alignment:1`、`newline:2`（中文標點換行）。
2. `bimteki:create_project_table_template` 一次送完整 cells，並帶 `merges=[{"row":0,"col":0,"colspan":2}]`（合併只能用這個參數）。`equal_col` 不必帶：預設 `[0,1]` 兩欄等寬即可，要左寬右窄才傳 `[0,0]`（別傳空陣列）。每格都已明確給 `charwidth:1` 或 `newline:2`，不要依賴預設。
3. `bimteki:modify_project_table_template` 補上：`template_name`「無障礙建築檢討表」（同名加日期後綴）、`column_widths=[520,480]`（條文欄較寬；只影響編輯器顯示）。
4. **驗證**：`bimteki:get_project_table_templates(template_guid=新guid)` 讀回，核對列數（標題＋條文數）、標題跨欄、左欄條文正確、右欄該綁 autotext 的格含 token、charwidth/newline/粗體。
5. **回報**：樣板名稱、哪些條綁了 autotext（列出對應欄位）、哪些退樣板句、**哪些格留佔位符（待手填清單，逐條標明）**，並提醒可在 BIMTeki 表格管理器放置到圖面。

## 儲存格寫法

- 固定文字：`{"row":1,"col":0,"text":"第167條：...","newline":2}`。
- 綁 autotext：
  ```json
  {"row":4,"col":1,"newline":2,
   "segments":[
     {"type":"text","value":"檢討：本案汽車車位設 "},
     {"type":"autotext","token":"${...汽車停車位數...}"},
     {"type":"text","value":" 輛，應設無障礙停車位 1 輛、本案設置 2 輛，符合規定。~ok"}]}
  ```
- 含佔位符：`{"segments":[{"type":"text","value":"檢討：本案非屬B-4組，故不適用。~ok"}]}`
- 格式欄位的值域與預設見 `../table/references/spoke-conventions.md` 第 5 節；本表用法：標題 `charwidth:1`、其餘 `newline:2`；合併只在 `merges`。所有內容屬專案層級，儲存格不需 storyGuid。

## 注意事項

- **不可捏造**外部引用；免檢討句（167-4/167-5/167-7）為常見預設，BIMTeki 無法驗證，回報時提醒使用者確認是否與本案相符。
- 右欄結尾「~ok」沿用來源範本慣例，使用者不需要可整批拿掉。
