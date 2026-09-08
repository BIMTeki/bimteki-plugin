# 檢討表 spoke 共用規範（前置檢查・autotext 原則・儲存格格式・建表流程）

**這份是各 `table-*` spoke（經 `table-area`／`table-code` 兩個分類 hub 路由，以及同樣建表的 `custom-area-review`）共用行為的單一事實來源。** 各 spoke 的 SKILL.md 只寫「這張表特有」的內容
（列組成、案型分支、token 對照、預設樣板名、欄寬），共通的流程與眉角一律指回這裡。
需求版本另見 `mcp-compat.md`；autotext 分類速查另見 `table-catalog.md`。

> **spoke 可以單獨呼叫，不需經過 `table-area`／`table-code` hub。** 本檔只是參考資料（跟 `mcp-compat.md` 一樣以相對路徑
> `../table/references/spoke-conventions.md` 讀取），不是流程入口。各 spoke 內文仍保留最關鍵的幾行眉角，
> 缺了本檔也不會失能，只是少了細節。
>
> **維護規則**：共通行為要改，改這裡一份；不要回各 spoke 各改一份（會漏改、會漂移）。
> 各 spoke 只有在「這張表的做法真的跟通則不同」時才在自己的 SKILL.md 寫例外，並註明是例外。

## 1. 前置檢查（標準順序）

1. **`bimteki:check_connection`**。多開 Archicad 時先 `bimteki:list_archicad_instances` 讓使用者確認要操作
   哪個專案，再 `bimteki:set_active_archicad_instance` 選定（或每次呼叫帶 `target_port`）；未選定時其他工具會回
   「偵測到多個 instance」錯誤。
   **版本關卡**：回傳最後一行「版本：」要看過（**沒有這行代表 MCP 早於 0.8.0，照常往下走、不要擋**）——
   使用者的 MCP／外掛隨安裝檔更新，跟 skill 常常不同期。需求版本與版本不足時的處理見 `mcp-compat.md`；
   真的版本不夠就停手請使用者重跑安裝檔，**不要改用舊流程默默把表建出來**（使用者會拿到一張跟預期不同的表卻不知道為什麼）。
2. **`bimteki:get_project_status`**（唯讀、成本低）：
   - `finalized`：已定案。只建樣板仍可做但要告知使用者；任何 `set_*` 寫回專案資訊會被拒絕。
   - `project_file.hasFile`：false＝專案只在記憶體中、變更無法落地 → 請使用者先「另存新檔」。
   - `has_unsaved_changes`：true → 先告訴使用者「建表會存檔，你目前未存的變更會一併落地」，讓他決定，不要默默存下去。
   - 回報未開啟 BIMTeki 專案 → 詢問專案路徑 → `bimteki:open_bimteki_project` → 重試。
3. **`bimteki:get_project_core_snapshot`** 讀案型與本案事實（各表要看哪些欄位見各 spoke）。
4. **面積類六張表（`table-area-*`）：確認區域已繪製並匯入 BIMTeki**——不經 hub 直接呼叫 spoke 時也要做。
   `bimteki:get_bimteki_zone_map`（唯讀）看 `counts`：面積總表、各層容積、地下層容積、屋突面積看 `void`（容積區域），
   建蔽率、基地概要看 `arch`（建蔽區域）；容積類另用 `bimteki:get_project_stories` 確認 `blocks[].stories` 有該建的樓層
   （`floors` 是 Archicad 骨架，不算）。要用的那一類是 0 就**停手**，告訴使用者「請先在 Archicad 繪製○○區域並匯入 BIMTeki」再回來：
   **區域一律由使用者自己畫、自己從面板匯入，skill 不代畫、不呼叫任何建立區域的工具、不建表**——區域缺席時建出來的表全是 0，
   日後補區域也不會自動變成正確版面（欄位與樓層列是建表當下決定的）。法規類三張表不做這一步。
5. **法規類三張表（`table-code-*`）：確認專案資料填寫齊全**——不經 hub 直接呼叫 spoke 時也要做。右欄大量引用專案資訊，
   資料沒填建出來就是一堆佔位符與「非…故免檢討」樣板句。讀 `bimteki:get_project_core_snapshot`（`site`／`building`，以各欄位 `text` 為準；
   空字串、`0`、「-」、「未匯入」都視為未填）、`bimteki:get_project_custom_params`（分類「建照審查資料」等，項目名稱慣例見
   `../../project-info-fill/references/field-routing.md` C 節）、`bimteki:get_project_stories`（各棟各層用途／戶數）。各表要看的欄位：

   | 表 | 基地／建築概要 | 自訂義參數（建照審查資料） | 其他 |
   |---|---|---|---|
   | 建照審查表（第 18～27 項） | 使用分區、基地面積、面前道路、用途組別、層數、棟數、戶數、建築高度 | 建築線判定、軍事禁限建判定、地質敏感區判定、地質技師公會核定函、都市計畫核准函、細部計畫開發方式、高度檢討圖號、畸零地基地寬度／深度／檢討圖號 | — |
   | 土管檢討表 | 使用分區、都市計畫名稱、基地面積、用途組別、建蔽率／容積率設計值 | 都市計畫發布文號、細部計畫開發方式（若土管條文引用） | 土地地號（`land.parcels`） |
   | 無障礙建築檢討表 | 用途組別、層數、戶數、建築高度 | — | 各層用途（`get_project_stories`） |

   缺漏時把缺的欄位（欄位名＋目前值）列成清單，**問使用者要走哪條**：(1) 先回填再建表——交給 `project-info-fill` 回填完再回來；
   (2) 照現況建表——缺的由 spoke 留佔位符或樣板句，回報時逐條列出「待人工填」；(3) 取消。**沒拿到答案不建表**；使用者選 (2) 時記下
   「哪些欄位確定留空」，不要建到一半再問。資料全部齊全時只說一句「已確認資料齊全」往下走。面積類六張表不做這一步。
6. **動手前告知使用者**：即將建立的樣板名稱（預設名見各 spoke）、判斷出的案型／版面／要建幾張、以及這是寫入專案並存檔的操作。
7. **模態視窗**：使用者在 Archicad 開著表格編輯器、設定等模態視窗時，MCP 會回報 modal dialog 錯誤——請他關掉再繼續。

## 2. 專案事實的唯讀工具（讀不到就退回，不要硬湊）

- **沒有 `get_project_info` 這個工具，不要呼叫。**
- `get_project_core_snapshot`：案型 `building.case_type`（`apartment`／`apartment_multi`／`small_house`／`small_house_multi`／`row_house`，
  另附 `is_row_house`）、`shared_hall`、`block_mode`、`block_count`、`story_count`、`land.*`、`review_settings.*`、造價區塊。
- `get_project_stories`：樓層骨架，逐棟逐層給 `isBasement`／`isRoof`／`isBetweenFloor`／`isSumStory`／`blockName`／`sortIndex`／`guid`
  （與 catalog 的 `storyGuidList`、求值工具同一組 GUID）；`floorHeight` 單位是**公分**。多棟時另有 `totalBlock`（「各棟總計」虛擬棟別，
  只有一般多棟才有，連棟透天沒有）。**要讀 `blocks[].stories`，不是 `floors`**——`floors` 是 Archicad 骨架，`blocks[].stories`
  才是 BIMTeki 實際建了資料的樓層；兩者有落差就列給使用者看（那幾層要先畫容積區域才有 storyGuid 可綁），不要拿別層 guid 硬湊。
  **用旗標判樓層角色，比用名稱字串比對可靠。**
- `get_bimteki_block_unit_settings`：各棟 `name`（A棟、B棟…）。
- `get_project_parking_info`：法定／實設車位數、地下層停車逐層明細。
- 綠化：無專屬讀取工具。面積走 `get_project_custom_area_review`（項目「綠化面積檢討」的區域組合），規定值走 `get_project_custom_params`（分類「綠化面積檢討」），基準空地走 coverage／siteOverview 既有 token；建表走 `custom-area-review` 的土管綠化案例。
- `get_project_custom_params`：使用者自訂義參數（欄位鍵 `CustomParam.{項目名}`）。
- `get_license_status`：授權方案（唯讀、不受授權閘門限制）。

## 3. 自動文字（autotext）原則

- **數值一律綁 autotext，由 BIMTeki 即時計算，不寫死**——即使當下能讀到數字算出結果也不寫，否則專案改動後表格不會跟著更新。
  優先序：**複合「算式：／計算式：」token**（同時含公式與結果）整格只用這一顆 → 只有分開的數值 token 才用文字運算符
  （`×`、`－`、`＝`）串接多個 autotext 自組，每個數值仍必須是 autotext → 連結果都沒有 token 時最後一段留
  `（請依左式計算後填入）`，不要自己算出數字填進去。
- **依數值變化的文字結論（符合／不符合、■□ 勾選）用判斷式** `{?條件|成立時|不成立時}`，不寫死建表當下的判定
  （條件規則同 `{=}` 公式；需**外掛 ≥ 0.0.23**，版本判斷見 `mcp-compat.md`，太舊就退回「結論不寫、只寫左式數值」）。
  門檻取大取小用公式內建的 `max`／`min`，級距或超過部分另計用數值 `if(條件, 值A, 值B)`（條件須為比較式，兩值只能是數字）。完整規則見 `../../custom-area-review/SKILL.md` 的公式與判斷式兩節。
- **Token 是專案特定的雜湊值，絕不憑記憶或跨案硬編**：一律以 `get_project_autotext_catalog(category=...)` 回傳的 `display`
  比對後取 `token`。例外：`customAreaReview` 由 `get_project_custom_area_review` 的 `zones[].token`／`groups[].token` 直接取，不掃 catalog。
  各表的 category 組合見各 spoke；分類速查見 `table-catalog.md`。
- **求值要挑對工具**：`evaluate_story_autotext_values` **只涵蓋 `storyArea`**；`coverage`／`volumeCheck`／`roofArea`／
  `customAreaReview`／`stairInfo` 等其他分類一律用通用版 `evaluate_autotext_values(category=...)`。**用錯不會報錯、只會回空**，
  很容易被誤判成 0。陣列自動文字無法求值（放到圖紙才展開），要數字改讀對應的唯讀工具（例如停車讀 `get_project_parking_info`）。
- **判 0 容差** `abs(value) < 0.005`。求值工具不可用或回錯時**不要臆測、不要用區域圖資硬湊**：跳過 0 值過濾、保留所有列／欄，
  並在回報明說「因數值取得失敗，本次未依 0 值移除」。
- **storyGuid／roomGuid**：`storyArea`、`roofArea` 等 story 相依 token（`targetTypeName: "story"`、`needGUID: true`）要在 cell 上帶
  `storyGuid`（樓層列用該層 guid；總計列用全案總計 guid——`storyGuidList` 裡單棟取唯一的「總計：」、多棟取**最後一個**「總計：」）。
  `roomGuid` 一律用常數 **`4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`**（所有 BIMTeki 檢討表都用它，直接照抄）。
  專案層級（`startmanager`）token 與固定文字格不需 storyGuid。
- 剛建立、未放置到圖面的樣板，`statedata` 會顯示原始 token 字串——這是**尚未評估的正常狀態**，核對以 `originaldata` 是否含正確 token 為準。

## 4. 佔位符與樣板句

- **不可捏造**：函號、核准日期、核准圖號、都計案名、地號、起造人、公告單價等 BIMTeki 無法得知的外部資訊，一律留佔位符，
  寧可留白讓使用者補，也不要編造看似合理的號碼或日期。慣例（方便事後尋找取代）：
  文號 `◯◯◯字第◯◯◯◯◯號`、日期 `○○○年○○月○○日`、圖號 `A0-○`／`A6-○`、其他 `◯◯◯`。
- **「非…故免檢討」類樣板句是常見預設，不是事實**：BIMTeki 無法驗證是否屬實（禁限建、農業區、B-4 組、無居室…），
  回報時逐項提醒使用者確認，不符就請他改。土管表例外：無法判斷者**留空**而非填免檢討句（見 `table-code-landuse`）。
- 右欄結尾的「~ok」／「...OK」沿用來源範本慣例；使用者不需要可整批拿掉。

## 5. 儲存格格式欄位（以外掛原始碼 `TJLTable.h` 的列舉為準）

| 欄位 | 值 | 預設 |
|---|---|---|
| `textbold` | `true` 粗體／`false` 正常 | `false` |
| `textsize` | `1` 標題字級／`2` 內容字級 | `2` |
| `alignment` | `1` 靠左／`2` 置中／`3` 靠右 | `1` |
| `charwidth` | `0` 正常／`1` 隨欄寬縮減 | **`1`（縮減）** |
| `newline` | `0` 不換行／`1` 運算符號（算式）換行／`2` 中文標點（「、」）換行／`3` 直接換行 | `0` |
| 框線值（`left_line`／`top_line`／`right_line`／`bottom_line`） | `0` 不畫／`1` 實線／`2` 隱藏線（虛線）／`3` 雙線／`4` 自訂線 | — |

- **`newline` 與 `charwidth: 1` 互斥**：`newline` 設非 0 會自動把 `charwidth` 歸 0；只設 `charwidth: 1` 則自動把 `newline` 歸 0。
- **create 對未指定的格預設 `charwidth: 1`（縮減字寬）**，因此**每一格都要明確給 `newline` 或 `charwidth`**，否則整張表會被非預期縮減字寬。
- ⚠️ 各 spoke 早期文件把 `newline: 1` 寫成「直接換行」、`2` 寫成「依中文換行」；依原始碼 **`1` 是運算符號換行、`3` 才是直接換行**。
  各表目前沿用實測過的值（兩欄法規表多用 1 或 2、容積／屋突值格用 3）；放置後若長句沒有如預期換行，改用 `3`。
- `textbold` 是**整格**屬性，無法只加粗其中一行；需要局部強調就拆成兩列（`table-floor-plan-code` 的做法）。
- 單格文字上限 2500 字，超過建立時即拒絕。
- `rowspan`／`colspan` **不要寫在 cell 上**（建立時會被忽略），合併只用 `merges` 參數。
- 標題與標籤中的全形空白（「各　層　樓　地　板　面　積」「小　計」）是排版慣例，照抄。

### segments 寫法速查

```json
{"row": 1, "col": 0, "text": "基地面積", "newline": 1}                                  // 固定文字
{"row": 4, "col": 1, "storyGuid": "{…樓層guid…}", "roomGuid": "4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3",
 "segments": [{"type": "autotext", "token": "${TJL$F…}"}]}                              // 純 autotext（story 相依）
{"row": 6, "col": 1, "newline": 2,
 "segments": [{"type": "text", "value": "檢討：本案位於 "},
              {"type": "autotext", "token": "${…使用分區…}"},
              {"type": "text", "value": "，符合規定。~ok"}]}                            // 混合文字
{"row": 10, "col": 1, "newline": 1,
 "segments": [{"type": "autotext", "token": "${…使用面積…}"}, {"type": "text", "value": "×"},
              {"type": "autotext", "token": "${…基準建蔽率…}"}, {"type": "text", "value": "＝"},
              {"type": "autotext", "token": "${…允建建築面積…}"}]}                     // 無複合 token 時自組算式
```

多項數值逐行呈現時用「標籤＋`\t`＋autotext」、行間 `\n`（土管、綠化表的寫法）。

## 6. 建表共通流程

1. **組 cells**：依本案判定後的動態列／欄**一次組好完整 cells**，不要分多次 create 產生多個殘缺樣板；create 失敗，修正後重試前先確認沒留下半成品。
   列數或欄數動態時，後續列的 row 索引、`merges`、`colspan` 要跟著位移，不要留空白列。
2. **`bimteki:create_project_table_template`** 一次帶齊 `cells`、`merges`、`equal_col`、框線（v0.7.1 起支援，不必再「先建再 modify 補」）。
   - `merges` 每筆 `{row, col, rowspan, colspan}`（0-based），只允許單列多欄或單欄多列，不可同時跨列跨欄、不可互相重疊。
   - `equal_col`：新建表格預設把所有欄設成強制等寬（讀回 `equalCol=[0,N-1]`），會蓋掉 `column_widths`。要解除就傳**非空的退化區間 `[0,0]`**
     （等寬群組只含第 0 欄＝欄間不再等寬）；**不要傳 `[]`**（舊版當成未提供、不生效）。要部分欄等寬就給該區間（例如土管表 `[1, 2]`）。
   - 每張表**只允許一個陣列自動文字**（`is_array_autotext_root`）。
   - 取回傳的 `nodeGuid`。
3. **`bimteki:modify_project_table_template`** 補 create 收不到的樣板層級屬性：
   - `template_name`：預設名見各 spoke；同名樣板已存在時加日期後綴避免混淆。
   - `column_widths`：**只影響編輯器顯示**，放置到圖面後的實際欄寬由 `equalCol` 決定。
   - `table_type`（`normal`／`story`）與 `story_guid`（story-open 樣板才設）。
   - 步驟 4 讀回發現 `merges`／`equal_col` 沒吃到才在此重送（`merges` 為整組取代）；格式沒生效用 `cells` patch 修正
     （只帶 row/col 與要改的格式欄位，內容會保留；帶完整 `segments`／`text` 則整格覆寫）。
   - 已放置到圖面的表格會自動同步（回傳 `placedTableCount`／`updatedPlacedTables`）。
   - **團隊協作**：modify 前會先整批保留所有已放置的表格；有表格被其他使用者保留時回傳 `lockedTables`（含 templateName／windowTitle／owner）
     **且不做任何修改** → 把清單轉告使用者，請持有者釋放後再重試，不要反覆重送硬闖。
4. **驗證**：`bimteki:get_project_table_templates(template_guid=新guid)` 讀回，核對列欄數、`merges`、各格 `originaldata` 含正確 token、
   該帶 storyGuid 的格帶對樓層、`textbold`／`charwidth`／`newline`、`equalCol`、`column_widths`。有出入用 modify 修正後再讀回確認。
   `statedata` 顯示原始 token 屬正常（見第 3 節）；要看實際數值用對應的求值工具，或放置到圖面。
5. **回報**（簡短）：樣板名稱；案型／版面判斷與依據；哪些格綁了 autotext（複合算式 token 特別標出）；哪些退回樣板句；
   **待手填清單**（逐格標明第幾列要補什麼）；哪些結論屬預設假設請使用者複核；提醒可在 **BIMTeki 表格管理器**放置到圖面。
   若 0 值過濾因求值失敗而略過，一併說明。

## 7. 寫入與刪除的底線

- 新建樣板會**寫入專案並存檔**，屬可逆性低的操作——動手前先讓使用者知道樣板名稱與判斷結果（第 1 節第 4 點）。
- **刪除舊樣板**（`manage_project_table_templates` 的 delete）必須先取得使用者明確同意；已放置到圖面者刪樣板後會轉為靜態表格，圖面元素需人工移除。
- **寫回專案資訊**（任何 `set_*`）一律先問過使用者；案件已定案時會被拒絕，直接留佔位符。
- **數值不對不要在表格裡硬改**：表格只是綁定，數值來自專案資料與區域；該改的是專案設定或容積區域，改完表格自動跟著更新。
