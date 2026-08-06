---
name: bimteki-per-floor-volume-review-table
description: 在 BIMTeki 專案中生成「各層容積檢討」表格（每一地上樓層一張 TableTemplate 表格樣板，俗稱 XX層容積檢討，建照圖說 A0-12~14）。當使用者說「做各層容積檢討表 / 建立地上層容積檢討 / 產生每層容積檢討 / per-floor volume review table」，或由 `table` skill 帶 `volume` 參數路由進來時使用本 skill，即使沒有明講「skill」二字。三欄式，分「當層樓地板面積(A)／免計容積(B)／回計容積(C)／(A)-(B)+(C)」四段，值欄全綁 storyArea「算式：」autotext。案型分支（單棟／一般多棟／連棟透天）、夾層合併版面、0 值列取捨與腳本用法見本文。屋突層與地下層另有專屬 skill，不要用本 skill 代替。
---

# BIMTeki 各層容積檢討表生成

在目前開啟的 BIMTeki 專案中，為**每一地上樓層**建立一張「XX層容積檢討」表格樣板。
每張表 3 欄（連棟透天為 3＋棟數欄），內容由上而下分四段：**當層樓地板面積(A)、
免計容積(B)、回計容積(C)、(A)-(B)+(C)**。值欄一律用 storyArea 的**「算式：」autotext**
綁定，數值由 BIMTeki 即時計算——**絕不要把當下讀到的數字寫死進儲存格**。

列/欄與項目出現與否會**依案型與各項面積是否為 0 動態調整**。完整結構規格見
`references/table-structure.md`；display→token 對照見 `references/tokens.md`；
儲存格由 `scripts/build_volume_table.py` 產生。本檔描述流程。

## 前置檢查

1. `bimteki:check_connection`。多開時會要求選 instance：先 `bimteki:list_archicad_instances`
   讓使用者確認要操作哪個專案，再 `bimteki:set_active_archicad_instance` 選定，或每次呼叫帶
   `target_port`。
   **版本關卡**：`check_connection` 回傳最後一行「版本：」要看過（**沒有這行代表 MCP 早於 0.8.0，照常往下走、不要擋**）——使用者的 MCP／外掛
   是隨安裝檔更新的，跟本 skill 常常不同期。需求版本與版本不足時的處理方式見
   `../table/references/mcp-compat.md`；版本不夠就停手請使用者重跑安裝檔，
   不要改用舊流程默默把表建出來（使用者會拿到一張跟預期不同的表卻不知道為什麼）。
2. `bimteki:get_project_status`（唯讀、成本低）確認專案狀態：`finalized`（已定案）、
   `project_file.hasFile`（false＝專案只在記憶體中、變更無法落地，請使用者先另存新檔）。
   回報未開啟 BIMTeki 專案就詢問路徑並用 `bimteki:open_bimteki_project` 開啟後重試。
3. 動手前先讓使用者知道：即將為哪些樓層各建一張表、判斷出的案型、以及會寫入專案並存檔。
   注意：若使用者在 Archicad 開著表格編輯器等「模態視窗」，MCP 會回報 modal dialog 錯誤——
   請他關掉該視窗再繼續。

## 判斷案型（決定組表方式）

呼叫 `bimteki:get_project_core_snapshot`，讀 `building`：
- `case_type`：**判斷案型（含連棟透天）一律以這個為準**。`apartment`=共用梯廳/單棟、
  `apartment_multi`=共用梯廳/多棟、`small_house`=非共用梯廳/單棟、`small_house_multi`=非共用梯廳/多棟、
  `row_house`=連棟透天（分棟檢討），另附 `is_row_house` 布林。
- `shared_hall.value`：`true`=共用梯廳、`false`=非共用梯廳（連棟透天固定視為非共用）。
- `block_mode.value`：`true`=多棟、`false`=單棟。
- `block_count.value`：棟數。

`case_type` 欄位不存在（面板尚未升級的舊版）時才退回結構判斷：`bimteki:get_project_stories` 有
`totalBlock`（「各棟總計」虛擬棟別，**只有一般多棟才有**）→ 有＝一般多棟、多棟但沒有＝連棟透天；
也可退而看 `get_project_autotext_catalog` 的 `storyGuidList` 有沒有「各棟總計地上X層」。
仍不確定就向使用者確認（使用者通常知道此案是不是連棟透天）。

多棟／連棟透天再用 `bimteki:get_bimteki_block_unit_settings` 取各棟 `name`（如 A棟、B棟）。

| 案型 | 每張表對應的樓層屬性 | 欄數 |
|----|----|----|
| 單棟（共用/非共用） | 各地上層自己的 story | 3 |
| 一般多棟（共用/非共用） | 各「各棟總計地上X層」story；室內面積/陽台面積/陽台>2m 展開各棟＋小計（項目名獨立欄垂直合併＋棟別欄，各棟列綁該棟該層 story） | 4 |
| 連棟透天 | 該層各棟的 story，一張表多欄 | 3＋棟數 |
| 單棟＋夾層 | mezz_single 版面：項目/當層/夾層/小計；室內面積/陽台面積/陽台>2m 三欄各自綁值，其餘項目綁小計並跨欄合併 | 4 |
| 一般多棟＋夾層 | mezz 版面：項目/棟別/當層/夾層/小計；分棟項綁各棟當層與夾層、合併項綁各棟總計小計 | 5 |

**重要**：夾層判斷與棟數無關——**只要該地上層存在配對的「…夾層」樓層，就一律改用夾層(mezz)版面**，
不論案型是單棟還是多棟。判斷案型（單棟/一般多棟/連棟透天）只決定「用哪一種 mezz 變體」（4 欄
mezz_single 或 5 欄 mezz），不能拿「這是單棟案」當理由跳過夾層規則、退回套用普通單層版面——
這是本 skill 曾經犯過的錯誤（見下方「注意事項」），修正前務必對照本節與第四點五／四點六節。

## 取得 token

`bimteki:get_project_autotext_catalog(category="storyArea")`，用 `references/tokens.md` 的
**display 名稱**比對取 `token`（值欄用「算式：」系列；標題用「樓層名稱」「棟別」；判 0 用「面積：」系列）。
`scripts/build_volume_table.py` 內含實測穩定的預設 token，但仍**建議比對確認**；有出入時把該案
實際 token 放進 config 的 `tokens` 覆寫，**不要憑記憶硬編**。

## 決定要建的樓層

- 只建**地上各層**（地上一層…地上N層，含夾層/小計等中間層）。
- **屋突層不建**（另有 bimteki-rooftop-area-review-table skill）。**地下層不建**（採地下層總量檢討時更不建；地下另有 6 欄式檢討表）。
- 單棟：取各地上層 story。一般多棟：取各「各棟總計地上X層」story，並另取各棟同層 story 供展開列用。
  連棟透天：把各棟同一層 story 分組（以樓層名稱去掉棟別前綴後相同者為同一層），每組一張多欄表。
- **有夾層的地上層一律改用夾層(mezz)版面，與單棟/多棟案型無關**：只要存在配對的「…夾層」樓層
  （單棟為「…小計」、一般多棟為「各棟總計…小計」），就不能把該層、其夾層、其小計當三個獨立樓層
  各建一張普通表——單棟用 4 欄 `mezz_single` 版面（見結構規格第四點六節），一般多棟用 5 欄 `mezz`
  版面（見第四點五節）。判斷順序：**先看樓層清單裡有沒有配對的「…夾層」，有的話直接進 mezz 分支；
  案型（單棟/多棟）只用來選 mezz_single 或 mezz 兩種變體之一，不是用來決定要不要用 mezz**。
- **樓層清單優先用 `bimteki:get_project_stories`**：它直接給每層的 `isBetweenFloor`（夾層）、`isRoof`
  （屋突）、`isBasement`（地下）、`isSumStory`、`blockName`、`sortIndex` 與 `guid`（與 `storyGuidList`、
  `evaluate_story_autotext_values` 同一組 GUID），**用旗標判夾層／屋突／地下層，比用樓層名稱字串比對可靠**。
  先掃一遍列出「哪些地上層有配對的夾層」，再決定每層用哪種版面。名稱比對只當旗標缺漏時的後備。
- 樓層清單的其餘挑法（各棟總計、小計節點對應）見 `references/table-structure.md` 第五節。

## 每層決定 A、B、C 段要出現哪些項目

當層樓地板面積(A) 的陽台相關列、免計容積(B) 與 回計容積(C) 的項目**依規則與是否為 0
動態增減**（規則見結構規格第三節）：

- **工廠類建築**：`get_project_core_snapshot` 的 `review_settings.balcony_in_floor_area.value`
  為 true（面板標籤「工廠類建築（陽台全額計入容積樓地板面積計算）」）時，陽台全額計入容積、
  不做 1/8 免計檢討——A 段只放「室內面積、陽台面積、當層樓地板面積」三列（移除 陽台>2M、
  室內1/8或8m²、陽台1/8檢討、陽台最終面積），config 加 `factory_mode:true`。
  可與下面的陽台過濾疊加：工廠類且陽台面積為 0 → A 段只剩「室內面積、當層樓地板面積」。
  另外，工廠類＋共用梯廳案型時，C 段不放「陽台10%檢討」（陽台已全額計入、無 10% 回計檢討；
  組 section_c 時直接略過該項，其餘共用回計項不受影響）。
- **A 段陽台過濾**：若該層陽台面積為 0（用「面積：陽台(原始)」判 0；catalog 無此 display 時改用
  「面積：陽台(最終)」），A 段不放「陽台面積、陽台>2M、室內1/8或8m²、陽台1/8檢討、陽台最終面積」
  五列，只留「室內面積、當層樓地板面積」，並在 config 加 `omit_balcony:true`（build 腳本會一併處理
  blockrows/mezz 版面）。一般多棟以「各棟總計該層」判斷；連棟透天對各棟該層都評估，
  **任一棟陽台>0 就保留全部陽台列**。
- **共用/非共用**：非共用時，B 段不放「梯廳」；C 段不放「當層樓地板面積10%、當層樓地板面積15%、
  梯廳10%檢討、陽台10%檢討、陽台+梯廳15%檢討」（這 5 項僅共用出現）。
- **0 值過濾**：用 `bimteki:evaluate_story_autotext_values`（帶該樓層 story guid 與各項的**「面積：」**
  token/display）取數值，`|value|<0.005` 視為 0 者不放該列。
  - B 段各項（機電設備、管道間、停車空間、騎樓、車道、防空避難室，共用另含梯廳）：面積>0 才放。
  - C 段：10%/15%/梯廳10%/陽台10%/陽台+梯廳15% 需「共用且（陽台或梯廳面積>0）」才放；
    **工廠類建築時「陽台10%檢討」一律不放**（即使共用且陽台>0）；
    停車空間回計需停車空間>0；裝飾柱回計需其面積>0。
  - 連棟透天多欄表：對**各棟該層**都評估，**任一棟該項>0 就放該列**（欄內各棟各自綁值）。
- (A)-(B)+(C) 不做 0 值過濾；A 段除上述陽台過濾外，其餘列（室內面積、當層樓地板面積）一律保留。

## 產生儲存格並建表

1. 依上面結果組出 `scripts/build_volume_table.py` 的 config JSON（欄位說明見結構規格第六節）：
   - 單棟（無夾層）：`mode:"single"`、`story_guid`＝該層。
   - 單棟＋夾層：`mode:"single"`、`mezzanine_single:{main=該層 story, mezz=該層夾層 story,
     subtotal=該層小計 story}`＋`title_story`＝main → 4 欄 mezz_single 版面。
   - 一般多棟（無夾層）：`mode:"single"`、`block_rows:{blocks:[{name,story_guid=該棟該層}...],
     subtotal_story=各棟總計該層}`（觸發 A 段前三項展開）。
   - 一般多棟＋夾層：`mode:"single"`、`mezzanine:{blocks:[...], subtotal_main=..., subtotal_mezz=...,
     subtotal_story=...}` → 5 欄 mezz 版面（見結構規格第四點五節）。
   - 連棟透天：`mode:"multiblock"`、`blocks:[{story_guid=該棟該層}...]`。
   執行取得 `{cells, merges, column_widths, cols, rows}`。
2. `bimteki:create_project_table_template(cells=..., merges=...)`——v0.7.1 起 create 已支援
   `merges` / `equal_col` / 框線參數，**合併直接在這一步帶進去**（每層一張表、張數多，省一次往返有感）。
   合併只能用 `merges` 參數；寫在 cell 上的 `rowspan`/`colspan` 建立時仍會被忽略。每格已明確給
   charwidth/newline，勿依賴預設。取回傳 `nodeGuid`。
3. `bimteki:modify_project_table_template(template_guid=新guid, template_name=...,
   column_widths=..., table_type="normal")` 補上 create 收不到的樣板名與欄寬（步驟 4 讀回發現
   `merges` 沒吃到才一併重送）。建議命名「地上X層容積檢討」，同名已存在加日期後綴。
   - **團隊協作要注意**：modify 前會先整批保留所有已放置的表格；若有表格被其他使用者保留，會回傳
     錯誤與 `lockedTables`（含 templateName／windowTitle／owner）**且不做任何修改** → 把清單轉告
     使用者，請持有者釋放後再重試。一次要建很多張時尤其要留意，別在同一個錯誤上重跑整批。
4. **驗證**：`bimteki:get_project_table_templates(template_guid=新guid)` 讀回，核對欄列數、merges、
   每格 originaldata 是否為正確 token、各值格 storyGuid 是否為該樓層（多棟展開列為各棟該層、
   小計為各棟總計；連棟透天各欄為各棟該層）。
   - **正常現象**：剛建立、未放置到圖面的樣板，`statedata` 會顯示原始 token 字串（尚未評估），
     核對以 `originaldata` 為準；要看實際數值用 `bimteki:evaluate_story_autotext_values` 另行確認。

## 儲存格寫法要點（與 references/table-structure.md 一致）

- 值格用 `segments`＋autotext token，並帶該樓層/該棟 `storyGuid` 與 `roomGuid`
  （固定常數 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`，所有 BIMTeki 容積檢討表都用它；直接照抄）。
- 全表 `alignment:1`（靠左）、`textbold:false`。區段標籤（col0）`charwidth:1`、`textsize:2`；
  項目名（col1）`charwidth:0`；值格 `charwidth:0`、`newline:3`；標題列 `textsize:1`。
- 標題只用「樓層名稱」autotext＋「容積檢討」（實測樓層名 token 回傳「地上二層」不含棟別，標題乾淨）。
- 區段標籤在 col0 用 `merges` 的 rowspan 涵蓋該段列數；(A)-(B)+(C) 只有 1 列不合併；標題列 colspan＝總欄數。
- (A)-(B)+(C) 最終列的段標籤**依是否有 B/C 段動態組**：「(A)」為底，有 B 加「-(B)」、有 C 加「+(C)」（build 腳本已自動處理）。

## 注意事項

- 本 skill 會**新建樣板並存檔**（可逆性低）；一次可能建很多張（每層一張），動手前先讓使用者確認
  樓層範圍與案型。刪除舊樣板（`manage_project_table_templates` 的 delete）必須先取得使用者明確同意。
- 逐張表完整組好再送 create，避免產生殘缺樣板；create 失敗先確認沒留半成品再重試。
- 若 `evaluate_story_autotext_values` 不可用，不要臆測數值：改為保留 A 段全部列與（非共用過濾後的）
  所有 B/C 項目，並在回報時說明「因數值取得失敗，本次未依 0 值移除項目」。
- **已知踩過的坑**：曾經在單棟＋夾層案子（如「地上四層」配對「地上四層夾層」＋「地上四層小計」）
  誤判為三個獨立樓層、各建一張普通 3 欄表。原因是把「案型（單棟/多棟）→ 版面」對照表跟「有無夾層
  → 要不要用 mezz」兩件事混為一談，看到「單棟」就直接套用單棟的預設處理、沒有另外檢查該層是否有
  配對的「…夾層」樓層。**判斷順序務必是：先掃樓層清單找配對的「…夾層」，有則一律走 mezz 分支
  （單棟用 mezz_single、多棟用 mezz），案型只用來選這兩種 mezz 變體之一——不能因為是單棟就跳過
  夾層檢查。** 建表前務必先完整列出樓層清單並標出哪些層有夾層，再決定每層要用哪種版面——
  用 `get_project_stories` 的 `isBetweenFloor` 旗標掃一遍最快，別只靠樓層名稱字串比對。
