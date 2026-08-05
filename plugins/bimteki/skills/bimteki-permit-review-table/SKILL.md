---
name: bimteki-permit-review-table
description: 在 BIMTeki 專案中生成「建造執照及雜項執照規定項目審查表」的通用查核項目表（俗稱建照審查表，涵蓋依建築法第三十四條第三項應由主管建築機關審查的第十八～二十七項共 10 條）。當使用者想要「生成建照審查表 / 建立建照審查查核表 / 做建照審查通用檢討表 / 產生建照規定項目審查表 / building permit review table」時務必使用本 skill，即使沒有明講「skill」二字。表格為兩欄式：第一列為大標題，第二列起每列一項；左欄為固定的法規檢討項目（第18~27項條文，逐字照抄），右欄為依本案填寫的檢討內容。本 skill 會先用 BIMTeki MCP 取得專案資訊（get_project_core_snapshot 等）與自動文字目錄（get_project_autotext_catalog），逐項組出右欄內容，優先序為：**能對應到自動文字者優先綁定 autotext（如使用分區、法定/設計建蔽率、法定/設計容積率、建築物用途、面前道路、基地尺寸），讓 BIMTeki 即時計算；無對應者填標準樣板句；外部文件引用（技師公會函號、都計函號、地方政府文號、核准日期、檢討圖圖號等 BIMTeki 無法得知的資訊）一律留明顯佔位符待人工填**。再用 create_project_table_template 一步建表（cells 與標題列跨欄 merges 一起送、每格明確給 charwidth），modify_project_table_template 補樣板名與欄寬，最後讀回驗證並回報待手填清單。本 skill 只負責「建照審查表（第18~27項查核項目）」；各層樓地板面積總表、容積區域繪製、門窗檢討、法規查詢另有各自的 skill，不要用本 skill 處理。
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

1. 呼叫 `bimteki:check_connection` 確認與 Archicad / BIMTeki Studio 的連線。
2. 呼叫 `bimteki:get_project_status`（唯讀、成本低）確認專案狀態：`finalized`（已定案）、`project_file.hasFile`（false＝專案只在記憶體中、變更無法落地，請使用者先另存新檔）。若回報未開啟 BIMTeki 專案，詢問使用者專案路徑後，用 `bimteki:open_bimteki_project` 協助開啟，再重試。
3. 動手前先讓使用者知道即將建立的樣板名稱（預設「建照審查表」），這是寫入專案的操作。

## 蒐集專案資訊

呼叫 `bimteki:get_project_core_snapshot`，讀取本案基本事實，作為判斷各項「該寫實際值還是免檢討句」的依據。至少關注：使用分區、法定/設計建蔽率、法定/設計容積率、基地面積與尺寸、面前道路、建築物用途（組別）。

需要更細的資料時，改用對應的專屬唯讀工具（**沒有 `get_project_info` 這個工具，不要呼叫**）：樓層骨架與各棟各層戶數/樓高/用途→`get_project_stories`；停車位數與停車檢討設定→`get_project_parking_info`；綠化→`get_project_green_info`；自訂義參數→`get_project_custom_params`。

**實際欄位以工具回傳為準**；讀不到的項目就退回樣板句或佔位符，不要硬湊。

## 取得自動文字目錄並比對

呼叫 `bimteki:get_project_autotext_catalog`。建議一次取這幾個分類即可涵蓋本表所需：`siteOverview,buildingOverview,coverage,volumeCheck`（即 `get_project_autotext_catalog(category="siteOverview,buildingOverview,coverage,volumeCheck")`）。掃描回傳項目的 `display` 名稱，針對 `references/items.md`「自動文字對應」表列出的 display 比對找出對應 `token`：

- **找到** → 該處用 autotext segment（`{"type": "autotext", "token": "..."}`）。
- **找不到** → 該處退回純文字：可帶入的實際值（從專案資訊讀到者）寫成文字，或依項目性質填樣板句／佔位符。

**Token 是專案特定的，絕對不要憑記憶或從其他專案硬編碼**；一律以 catalog 回傳的 display 比對後取用 token。建蔽率、容積率、使用分區、用途這類容積檢討核心欄位通常有 autotext，應優先綁；面前道路寬、畸零地最小寬深、都計/技師公會/地方政府函號等，多半沒有，依 `references/items.md` 的樣板句或佔位符處理。

## 逐項組內容

依 `references/items.md`，組出 10 列（第十八～二十七項）。每列：

- **左欄（col 0）**：固定條文文字，含「第XX項：」前綴，逐字照抄，不要改寫或精簡。
- **右欄（col 1）**：依優先序 autotext > 樣板句 > 佔位符 組出 segments；長句用 `newline: 2`（依中文換行）。

佔位符慣例（方便事後尋找取代）：文號 `◯◯◯字第◯◯◯◯◯號`、日期 `○○○年○○月○○日`、圖號 `A0-○`。第二十三項右欄的「規定值／本案設計」小表以文字列呈現（見 items.md），不使用巢狀子表。

## 建表流程

沿用 BIMTeki 表格樣板的已知眉角（與面積總表相同）：

1. **組 cells**：
   - Row 0：大標題，放在 col 0，內容為兩行標題（用單一 `\n` 手動斷行）；於步驟 3 以 merges 跨 2 欄。標題格 `textbold: true`、`textsize: 1`、`alignment: 1`（靠左）、**`charwidth: 1`（縮減字寬）**。設 `charwidth: 1` 會自動把 `newline` 取消為 0，兩行仍靠 `\n` 手動斷行、彼此不空行。
   - Row 1~10：col 0 左欄項目與 col 1 右欄內容皆 `alignment: 1`（靠左）、**`newline: 1`（直接換行）**。設 `newline: 1` 會自動把 `charwidth` 取消為 0（正常字寬）。
2. 呼叫 `bimteki:create_project_table_template` 一次送入所有 cells，**並同時帶 `merges=[{"row": 0, "col": 0, "colspan": 2}]`**（v0.7.1 起 create 已支援 `merges` / `equal_col` / 框線參數，合併不必再留到 modify）。**注意**：
   - **合併只能用 `merges` 參數**；寫在 cell 上的 `rowspan` / `colspan` 建立時仍會被忽略。
   - **`newline`（換行）與 `charwidth: 1`（縮減字寬）互斥**：設換行會自動取消縮減字寬、只設縮減字寬則自動取消換行。本表刻意用此特性——標題要縮減字寬故設 `charwidth: 1`；其餘格要直接換行故設 `newline: 1`。
   - create 對未指定 `newline`/`charwidth` 的格，`charwidth` **預設為 1（縮減字寬）**；因此每一格都要明確給定（標題 `charwidth: 1`、其餘 `newline: 1`），否則內容格會被非預期地縮減字寬。
3. 從回傳取得新樣板 guid，呼叫 `bimteki:modify_project_table_template` 補上 create 收不到的樣板層級屬性：
   - `template_name`：預設「建照審查表」；若同名樣板已存在，加日期後綴避免混淆。
   - **團隊協作要注意**：modify 前會先整批保留所有已放置的表格；若有表格被其他使用者保留，會回傳錯誤與 `lockedTables`（含 templateName／windowTitle／owner）**且不做任何修改** → 把清單轉告使用者，請持有者釋放後再重試。
   - `column_widths`：長度 2（起始 `[430, 470]`）。**注意：column_widths 只影響「編輯器顯示」，不影響放置到圖面後的 GDL 表格欄寬。**
   - **放置後的實際欄寬由 `equalCol` 決定**：新建表格預設 `equalCol=[0,1]`（兩欄等寬各半）。若使用者要左右不等寬，需另行調整 `equal_col`（把不要等寬的欄排除在範圍外）；一般兩欄式建照審查表用等寬即可。
   - 若 create 階段有格式沒生效（例如 charwidth），一併在此以 `cells` patch 修正（只帶 row/col 與要改的格式欄位，內容會保留）。
   - patch 既有格內容時：帶該格完整 `segments`（或 `text`）即整格覆寫；已放置於圖面的表格會自動同步更新（回傳 `updatedPlacedTables`）。
4. **驗證**：用 `bimteki:get_project_table_templates(template_guid=新guid)` 讀回，逐項核對：列數（標題 + 10 項 = 11 列）、標題跨欄合併、左欄條文文字正確、右欄該綁 autotext 的格是否含正確 token、charwidth/newline/粗體。有出入用 modify 修正後再讀回。
   - 已知現象：剛建立的樣板 `statedata` 會顯示原始 token 字串，這是尚未評估的正常狀態，放到圖面後才會解析成實際值；核對以 `originaldata` 是否含正確 token 為準。
5. **回報**：向使用者簡短說明——樣板名稱、哪些項用了 autotext（列出對應欄位）、哪些項退回樣板句、**哪些格留了佔位符（列成「待手填清單」逐項標明第幾項要補什麼）**，並提醒可在 BIMTeki 表格管理器放置到圖面。

## 儲存格寫法

- **固定文字**：`{"row": r, "col": c, "text": "第二十項：基地符合禁限建規定。", "newline": 1}`（內容格用 `newline: 1` 直接換行）。
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
- **格式欄位**（可與內容並列於同一 cell）：`textbold`(粗體)、`charwidth`(0 正常／1 縮減字寬)、`newline`(0 不換行／1 直接換行／2 依中文換行)、`alignment`(1 靠左／2 置中)、`textsize`(1 大，僅標題／2 一般)、`rowspan`/`colspan`(合併，於 modify 設)。本表用法：標題 `charwidth: 1`、其餘 `newline: 1`。
- startmanager/專案層級 autotext 不需 storyGuid；本表所有內容皆屬專案層級，儲存格不需帶 storyGuid。

## 注意事項

- **不可捏造**：函號、核准日期、核准圖號、都計案名等外部資訊 BIMTeki 無法得知，一律留佔位符，寧可留白讓使用者補，也不要編造看似合理的號碼或日期。
- **免檢討句是預設假設**：第二十項（禁限建）、第二十二項（農業區）等「非…故免檢討」是常見預設，BIMTeki 無法驗證是否屬實。若與本案實情不符（例如基地確實位於禁限建範圍），請使用者修正——回報時提醒這幾項屬預設假設。
- 新建樣板會寫入專案並存檔，屬可逆性低的操作；若要刪除舊樣板（`manage_project_table_templates` 的 delete）必須先取得使用者明確同意。
- 一次組好完整 cells 再送出 create，不要分多次產生殘缺樣板；create 失敗，修正後重試前先確認沒有留下半成品樣板。
- 右欄結尾的「~ok」沿用來源範本慣例；若使用者不需要可整批拿掉。
