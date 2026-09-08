---
name: table-code-permit
description: 在 BIMTeki 專案中生成「建造執照及雜項執照規定項目審查表」的通用查核項目表（俗稱建照審查表，第十八～二十七項共 10 條）。當使用者說「生成建照審查表 / 建立建照審查查核表 / 產生建照規定項目審查表 / building permit review table」，或由 `table-code` skill 帶 `permit` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。兩欄式，左欄為固定條文逐字照抄，右欄依本案填寫：能綁 autotext 者優先綁、無對應者填標準樣板句、外部文號日期一律留佔位符待人工填。逐項內容與 MCP 呼叫順序見本文。土管、無障礙、面積總表另有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 建照審查表生成

在目前開啟的 BIMTeki 專案中，建立一份兩欄式「建造執照及雜項執照規定項目審查表」的通用查核項目表（建照審查表）。固定 10 列項目（第十八～二十七項），左欄為法規條文（逐字照抄、不改字），右欄「檢討內容」依本案填寫。

右欄組法邏輯的優先序是本 skill 的核心：

1. **能綁自動文字（autotext）就綁** —— 讓 BIMTeki 即時計算，不要把當下讀到的數字寫死。
2. **沒有對應 autotext 就填標準樣板句** —— 依本案事實選「帶入實際值」或「非…故免檢討」。
3. **外部文件引用一律留明顯佔位符** —— 函號、日期、核准圖號等 BIMTeki 無法得知的資訊，絕不臆測或捏造。

每一項的固定條文、需要的資料、autotext 比對關鍵字、樣板句與佔位符寫法，**以 `references/items.md` 為準**；本檔描述流程。

> 需求前提：本 skill 需連上使用者本機的 Archicad + BIMTeki Studio 才能實際執行（MCP 工具會操作本機專案）。

## 前置檢查

標準順序與細節見 `../table/references/spoke-conventions.md` 第 1 節，摘要：

1. `bimteki:check_connection`（多開時先選 instance）。**版本關卡**：回傳最後一行「版本：」要看過——沒有這行代表 MCP 早於 0.8.0，照常往下走；需求版本與不足時的處理見 `../table/references/mcp-compat.md`，版本不夠就停手請使用者重跑安裝檔，不要改用舊流程默默建表。
2. `bimteki:get_project_status`：`finalized`／`project_file.hasFile`／`has_unsaved_changes`；未開啟專案就問路徑後 `bimteki:open_bimteki_project` 再重試。
3. **專案資料是否填寫齊全**（共用規範第 1 節第 5 步）：讀 `get_project_core_snapshot`（使用分區、基地面積、面前道路、用途組別、層數、棟數、戶數、建築高度）與 `get_project_custom_params`（建築線判定、軍事禁限建判定、地質敏感區判定、地質技師公會核定函、都市計畫核准函、細部計畫開發方式、高度檢討圖號、畸零地相關），缺的列出來問使用者：先回填（`project-info-fill`）／照現況建表留佔位符／取消；沒答案不建表。
4. 動手前告知即將建立的樣板名稱（預設「建照審查表」）與判斷結果，這是寫入專案並存檔的操作；使用者開著表格編輯器等模態視窗時請他先關掉。

## 蒐集專案資訊

呼叫 `bimteki:get_project_core_snapshot`，讀取本案基本事實，作為判斷各項「該寫實際值還是免檢討句」的依據。至少關注：使用分區、法定/設計建蔽率、法定/設計容積率、基地面積與尺寸、面前道路、建築物用途（組別）。

需要更細的資料時，改用對應的專屬唯讀工具（**沒有 `get_project_info` 這個工具，不要呼叫**）：樓層骨架與各棟各層戶數/樓高/用途→`get_project_stories`；停車位數與停車檢討設定→`get_project_parking_info`；綠化面積→`get_project_custom_area_review`（項目「綠化面積檢討」）；自訂義參數→`get_project_custom_params`。

**實際欄位以工具回傳為準**；讀不到的項目就退回樣板句或佔位符，不要硬湊。

## 取得自動文字目錄並比對

呼叫 `bimteki:get_project_autotext_catalog`。建議一次取這幾個分類即可涵蓋本表所需：`siteOverview,buildingOverview,coverage,volumeCheck`（即 `get_project_autotext_catalog(category="siteOverview,buildingOverview,coverage,volumeCheck")`）。掃描回傳項目的 `display` 名稱，針對 `references/items.md`「自動文字對應」表列出的 display 比對找出對應 `token`：

- **找到** → 該處用 autotext segment（`{"type": "autotext", "token": "..."}`）。
- **找不到** → 該處退回純文字：可帶入的實際值（從專案資訊讀到者）寫成文字，或依項目性質填樣板句／佔位符。

**Token 是專案特定的，絕對不要憑記憶或從其他專案硬編碼**；一律以 catalog 回傳的 display 比對後取用 token。建蔽率、容積率、使用分區、用途這類容積檢討核心欄位通常有 autotext，應優先綁；面前道路寬、畸零地最小寬深、都計/技師公會/地方政府函號等，多半沒有，依 `references/items.md` 的樣板句或佔位符處理。

## 逐項組內容

依 `references/items.md`，組出 10 列（第十八～二十七項）。每列：

- **左欄（col 0）**：固定條文文字，含「第XX項：」前綴，逐字照抄，不要改寫或精簡。
- **右欄（col 1）**：依優先序 autotext > 樣板句 > 佔位符 組出 segments；長句用 `newline: 2`（中文標點換行）。

佔位符慣例（方便事後尋找取代）：文號 `◯◯◯字第◯◯◯◯◯號`、日期 `○○○年○○月○○日`、圖號 `A0-○`。第二十三項右欄的「規定值／本案設計」小表以文字列呈現（見 items.md），不使用巢狀子表。

## 建表流程

共通眉角（create 一次帶齊 `merges`／`equal_col`、每格明確給 `newline` 或 `charwidth`、modify 補樣板層級屬性、`lockedTables`、驗證看 `originaldata`）見 `../table/references/spoke-conventions.md` 第 5～6 節；下面只列本表特有的設定。

1. **組 cells**：
   - Row 0：大標題，放在 col 0，內容為兩行標題（用單一 `\n` 手動斷行），以 `merges` 跨 2 欄。標題格 `textbold: true`、`textsize: 1`、`alignment: 1`（靠左）、**`charwidth: 1`（縮減字寬）**；設 `charwidth: 1` 會自動把 `newline` 歸 0，兩行仍靠 `\n` 手動斷行、彼此不空行。
   - Row 1~10：col 0 左欄項目與 col 1 右欄內容皆 `alignment: 1`（靠左）、**`newline: 1`**（設 `newline` 會自動把 `charwidth` 歸 0，即正常字寬）。
2. `bimteki:create_project_table_template` 一次送入所有 cells，並帶 `merges=[{"row": 0, "col": 0, "colspan": 2}]`（合併只能用這個參數，cell 上的 `rowspan`/`colspan` 會被忽略）。每格都已明確給 `charwidth: 1` 或 `newline: 1`，不要依賴預設。
3. `bimteki:modify_project_table_template` 補上：`template_name`（預設「建照審查表」，同名加日期後綴）、`column_widths=[430, 470]`（只影響編輯器顯示）。放置後的實際欄寬由 `equalCol` 決定，新表預設 `[0,1]` 兩欄等寬——一般兩欄式建照審查表用等寬即可，使用者要左右不等寬才另傳 `equal_col`。
4. **驗證**：`bimteki:get_project_table_templates(template_guid=新guid)` 讀回核對：列數（標題 + 10 項 = 11 列）、標題跨欄合併、左欄條文文字正確、右欄該綁 autotext 的格含正確 token、charwidth/newline/粗體。有出入用 modify 修正後再讀回。
5. **回報**：向使用者簡短說明——樣板名稱、哪些項用了 autotext（列出對應欄位）、哪些項退回樣板句、**哪些格留了佔位符（列成「待手填清單」逐項標明第幾項要補什麼）**，並提醒可在 BIMTeki 表格管理器放置到圖面。

## 儲存格寫法

- **固定文字**：`{"row": r, "col": c, "text": "第二十項：基地符合禁限建規定。", "newline": 1}`（內容格用 `newline: 1`）。
- **純自動文字**：用 segments 帶 token：
  ```json
  {"row": 6, "col": 1, "newline": 1,
   "segments": [
     {"type": "text", "value": "檢討：本案位於 "},
     {"type": "autotext", "token": "${...使用分區...}"},
     {"type": "text", "value": "，用途 "},
     {"type": "autotext", "token": "${...用途組別...}"},
     {"type": "text", "value": "使用，符合規定。~ok"}
   ]}
  ```
- **含佔位符**：把 BIMTeki 無法得知的外部引用寫成佔位符文字段：
  ```json
  {"segments": [
    {"type": "text", "value": "檢討：本案非位於軍事禁限建範圍，故免檢討。~ok"}
  ]}
  ```
- **格式欄位**的值域與預設見 `../table/references/spoke-conventions.md` 第 5 節。本表用法：標題 `charwidth: 1`、其餘 `newline: 1`；合併只在 `merges`。
- startmanager/專案層級 autotext 不需 storyGuid；本表所有內容皆屬專案層級，儲存格不需帶 storyGuid。

## 注意事項

- **不可捏造**：函號、核准日期、核准圖號、都計案名等外部資訊 BIMTeki 無法得知，一律留佔位符，寧可留白讓使用者補，也不要編造看似合理的號碼或日期。
- **免檢討句是預設假設**：第二十項（禁限建）、第二十二項（農業區）等「非…故免檢討」是常見預設，BIMTeki 無法驗證是否屬實。若與本案實情不符（例如基地確實位於禁限建範圍），請使用者修正——回報時提醒這幾項屬預設假設。
- 右欄結尾的「~ok」沿用來源範本慣例；若使用者不需要可整批拿掉。
