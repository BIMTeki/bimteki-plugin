---
name: custom-area-review
description: 在 BIMTeki 專案中依使用者提供的「檢討方式」檢討自訂面積項目（配合外掛的「自訂面積項目檢討」功能，主選單與面板同名；程式內部舊稱「自訂區域檢討」；適用地方特別法規等建照固定檢討表未涵蓋的面積比例檢討，例：台中宜居建築垂直綠化）。當使用者說「做自訂面積項目檢討 / 做自訂區域檢討 / 檢討自訂面積 / 面積比例檢討 / 特定檢討項目 / 依這個檢討方式幫我檢討 / 宜居建築檢討 / custom area review」，或提供一段自訂的面積比例檢討需求並表示已（或可以）在 Archicad 選好區域／填充時使用本 skill，即使沒有明講「skill」二字。需求三件事：檢討方式（必）、在 Archicad 選取好區域或填充（必）、呈現格式（選）；本 skill 會建立**一個**總檢討項目，把各組面積以「散裝區域」或「區域組合」掛在該項目底下，取得面積 autotext token（組合出一顆合計 token，另有計算式 token），最後把比例檢討組成表格樣板放到圖面。不經 `table` hub，直接呼叫本 skill。建蔽率、容積、屋突等建照固定檢討表另有專屬 skill，不要用本 skill 代替；土管的綠化面積檢討（綠化率、喬木株數）沒有專屬 skill，用本 skill 依「常見案例：土管綠化面積檢討」的固定命名建。
---

# BIMTeki 自訂面積項目檢討

地方特別法規（例：台中宜居建築的垂直綠化比、各縣市自治條例的特殊面積比）常要求「某類面積 ÷ 另一類面積 ≧ 規定值」這類**固定檢討表沒有涵蓋**的檢討。本 skill 用外掛的「自訂面積項目檢討」功能完成整條流程：

1. 依使用者的**檢討方式**建立**一個**總檢討項目（**不是**一組面積一個項目，見第一步）。
2. 各組面積掛在該項目底下：單顆＝**散裝區域**；多顆構成同一個量＝**區域組合**（一顆合計 token＋兩顆計算式 token，成員不出）。
3. 區域／組合自動成為**面積自動文字**；token 綁「項目＋區域／組合」GUID，改名不影響。
4. 以 token（必要時加 `{=...}` 公式；符合／不符合的結論用 `{?...}` 判斷式）組出比例檢討，建成表格樣板。

> **名稱**：使用者看到的正式名稱是「**自訂面積項目檢討**」——主選單字串、面板標題「BIMTeki自訂面積項目檢討」、autotext 分類顯示名、授權訊息全都是這個。「自訂區域檢討」只存在於程式內部註解，**對使用者說話時不要用**（使用者這樣講時聽得懂即可）。
>
> 需求前提：本 skill 需連上使用者本機的 Archicad + BIMTeki Studio；且使用者的訂閱需含「自訂面積項目檢討」模組授權（見前置檢查 3）。

## 前置檢查

1. `bimteki:check_connection`（多開時先選 instance；標準前置檢查見 `../table/references/spoke-conventions.md` 第 1 節）。
   **版本關卡（本表例外，需求比通則高）**：`get_project_custom_area_review`／`set_project_custom_area_review` 是 **MCP ≥ 0.11.0** 才有的工具，而本 skill 用到的**區域組合**（`create_group` 等 5 個 action）要 **MCP ≥ 0.12.0**（需求版本以 `../table/references/mcp-compat.md` 為準）。判斷方式：**工具清單裡找不到這兩支工具＝版本太舊**；找得到、但 `set_project_custom_area_review` 的說明沒有 `create_group` ＝ 只有 0.11.x，多顆面積只能退回 `{=a+b+c}` 湊合計（要跟使用者說明這是版本限制）。兩種情況都請使用者重跑最新版 BIMTeki Studio 安裝檔後**完全重開 Claude**，不要改用其他工具拼湊替代流程。
   > 註：MCP 是獨立 process，重跑安裝檔後沒有完全重開 Claude 的話，工具說明會停留在舊版（曾發生「原始碼有 `create_group`、工具說明卻沒有」的誤判）。
2. 呼叫 `bimteki:get_project_status`（唯讀）：`finalized` 為真代表案件已定案，**寫入會被拒絕**——直接告知使用者本 skill 無法在定案狀態下匯入區域，結束；`project_file.hasFile` 為假請使用者先「另存新檔」；`has_unsaved_changes` 為真先告知會一併存檔；未開啟專案則詢問路徑後 `bimteki:open_bimteki_project`。
3. **授權把關**：兩支工具回傳 `error_code="feature_not_licensed"` 時，代表使用者的訂閱不含「自訂面積項目檢討」模組（**試用方案不含此模組**，即使 `check_connection` 回「授權正常」也一樣被擋）。直接轉告工具回的原句「目前訂閱不包含『自訂面積項目檢討』授權，請聯絡 BIMTeki 客服升級方案」，**不要**嘗試用其他工具繞過。想講清楚是哪種授權狀態可加呼叫 `bimteki:get_license_status`（唯讀、不受授權閘門限制）看 `plan`／`is_trial`／`trial_ends_at`。
4. 動手前先讓使用者知道：將建立哪些檢討項目（名稱）、最後的樣板名稱——匯入與建表都會寫入專案並存檔。

## 收集需求（三件事）

- **檢討方式（必）**：使用者用自己的話描述，例「垂直綠化面積 ÷ 綠化基準面積 ≧ 10%」。從中萃取：需要幾**組**面積、各組的名稱、比例算式與規定值、判定方向（≧／≦）。規定值屬法規事實，**以使用者提供為準，不要臆測**；沒給就問。
- **選取好區域或填充（必）**：使用者尚未畫好就先停在這一步請他準備；區域用 Zone 或 Hatch 皆可（混選也可，非區域／填充的元素會被自動略過）。**填充名稱標好（例「GA：綠化面積」）時只需選一次**，可照名稱分組後帶 GUID 一次掛完；沒標名稱才需逐組選取（見第二步的 A／B 兩種掛法）。
- **呈現格式（選）**：檢討結果最後以表格樣板放到圖面；使用者有指定格式（欄位、列序、樣式）就照做，沒有就用下方「預設版式」。

## 第一步：規劃項目結構（一個檢討＝一個項目）

- **一個檢討方式＝一個檢討項目**，名稱用整個檢討的名字（例「垂直綠化設施面積」）。**不要**把檢討方式裡的每一組面積各建一個項目——那會讓面板長出一堆碎項目，也不是使用者的心智模型。
- 檢討方式裡的各組面積（GA／A／SGA／SA 之類）掛在**同一個項目底下**，靠**區域／組合名稱**區分：

  | 該組的組成 | 掛法 | token |
  |---|---|---|
  | 只有 1 顆區域／填充 | **散裝區域**（`add_zones`／`import_selected`） | 自己一顆 |
  | **多顆**區域／填充合起來算一個量 | **區域組合**（`create_group`） | 整組一顆**合計**＋兩顆**計算式**（`a+b+c = sum m²`／含成員名稱），成員不出 token |

  多顆時**優先用區域組合**，不要改成在表格裡寫 `{=a+b+c}`：合計由外掛算，日後增減成員不必改表。
- 區域／組合名稱就是 autotext 的欄位名，所以**請使用者在 Archicad 就把填充的 ID／名稱標好**（例「GA：綠化面積」）。名稱標好時可用 `add_zones`／`create_group` 帶 GUID 一次分完，不必逐組要使用者重新選取（見第二步）。
- 先呼叫 `bimteki:get_project_custom_area_review` 看現況（read-modify-write）：同名項目已存在時**不要重建**——問使用者是沿用該項目（可續匯入或先 `clear_zones`）還是換名稱。
- **面積來源**：預設 `original`（區域面積＝元素測量面積）。只有使用者明確說要用「面積分割」工具寫入的分割面積時才 `set_area_source` 為 `overwrite`；此設定影響**該項目所有區域與組合** token 的取值（沒經過面積分割的填充 `splitArea` 是 0，誤設成 `overwrite` 會全部顯示 0）。

## 第二步：把區域掛進項目

### `set_project_custom_area_review` 的 actions 一覽

| action | 用途 |
|---|---|
| `create_item`／`rename_item`／`delete_item` | 建／改名／刪檢討項目（刪項目連帶清掉其區域與組合） |
| `set_area_source` | 切該項目的面積來源（`original`／`overwrite`） |
| `import_selected` | 把**目前 Archicad 選取**匯入項目（**散裝**） |
| `add_zones`／`remove_zones`／`clear_zones` | 以 GUID 增／刪散裝區域；`clear_zones` 只清散裝、**不動組合** |
| `create_group` | 建立**區域組合**，`from_selection: true` 或 `guids` 擇一；`name` 可省略（自動「組合N」，但**建議明確命名**，那就是 autotext 欄位名） |
| `rename_group`／`delete_group` | 組合改名／刪除 |
| `add_zones_to_group`／`remove_zones_from_group` | 對組合成員增刪 |

「定位」＝ `itemId`（優先、不受改名影響）或 `itemName`；「組合定位」＝ `groupId`（優先）或 `groupName`（同項目內須唯一命中）。actions 依序執行、**all-or-nothing**：任一動作無效整批不套用，依回傳的 `errors` 修正後重送。

### ⚠️ `create_group` 不會把成員從散裝清單移除

外掛的 `CreateGroup` 只寫 `group.zones`、**完全不動 `item->zones`**。所以同一顆填充若已經 `add_zones`／`import_selected` 進散裝，再拿去 `create_group`，會變成「散裝 1 份 ＋ 組合 1 份」同時掛著、**面積被算兩次**。

- 正解：**確定要成組的填充直接 `create_group`，不要先 `add_zones`**。
- 已經誤放的：`remove_zones` 把散裝那幾顆移掉即可（組合不受影響）。
- 自檢：`get_project_custom_area_review` 的 `zoneCount` **含組合成員**，若「散裝顆數＋所有組合成員數」跟它對不上，或 `evaluate_autotext_values` 的欄位數多於「散裝顆數＋組合數」，就是有重複。

### 兩種掛法

**A. 填充已標好名稱（優先走這條）**：用 `bimteki:return_guid_of_selected_elements` 取選取，再用 `mcp__archicad-mcp__GetDetailsOfElements` 讀每顆的 `id`（＝填充名稱），照名稱分組，一次把 `create_item` ＋ `add_zones` ＋ `create_group` 送完。使用者只要選一次。**分組結果要先列給使用者確認再送**。

```
bimteki:set_project_custom_area_review(actions=[
  {"action": "create_item", "name": "垂直綠化設施面積"},
  {"action": "add_zones",   "itemName": "垂直綠化設施面積", "guids": ["<GA>", "<A>", "<SGA>"]},
  {"action": "create_group","itemName": "垂直綠化設施面積", "name": "SA：降版面積",
   "guids": ["<SA1>", "<SA2>", "<SA3>"]}
])
```

**B. 沒標名稱／使用者要逐組選**：一組一輪，**每輪都等使用者選取完成才呼叫工具**：

1. 請使用者選取該組的區域／填充（講清楚現在要選哪一組）。
2. 單顆的組送 `import_selected`；多顆的組送 `create_group` ＋ `"from_selection": true`。
3. 用回傳的 `importedCount`／`skippedNotZoneOrHatch`（非區域／填充）／`skippedDuplicate` 回報，**數量與使用者預期不符就停下來確認**，不要帶著錯的資料往下走。
4. 下一組，重複 1~3。

### 收尾

- 「目前 Archicad 中沒有選取任何元素」的錯誤＝使用者還沒選（或選取已被清掉），回到選取那一步。
- 全部掛完呼叫 `bimteki:get_project_custom_area_review` 總覽一次，把散裝區域與各組合（名稱＋面積＋成員數）唸給使用者確認，並做上面的 `zoneCount` 自檢。

## 第三步：取 token（不經 catalog）

`get_project_custom_area_review` 回傳的 `zones[].token`（散裝區域）與 `groups[].token`（區域組合合計）就是面積自動文字，**直接使用**，不需要再掃 `get_project_autotext_catalog` 比對顯示名（同名區域在 catalog 裡分不出來，這裡以 GUID 分）。

- **組合成員沒有 token**（`groups[].zones[]` 沒有 `token` 欄）。組合本身有三顆：`token`（合計）、`formulaToken`（計算式 `a+b+c = sum m²`）、`formulaWithZoneNameToken`（每項後綴成員名稱）——表上要列出組成時直接用計算式 token，不要自己逐顆拼；公式與判斷式裡一律用合計 `token`。
- **token 綁「項目＋區域／組合」GUID**：項目、區域、組合改名都不影響已放置的 token；但**同一顆填充掛到不同項目底下會拿到不同的 token**，換掛法（散裝↔組合）也會換 token。
  > 所以**項目結構要先定案再建表**。先建表後改結構，等於表格引用了失效 token，圖面上那些格子會變空字串。非改不可時的順序是：**新結構建好 → 取新 token → 改表 → 最後才刪舊項目／舊掛法**。
- token 依項目的 `areaSource` 求值（`zoneArea` 或 `splitArea`；組合為合計），切換面積來源 token 不變。
- token 是專案特定的，**絕不跨案硬編**；每次建表前重新取。
- 要先看數值可用 `bimteki:evaluate_autotext_values(category="customAreaReview")`（判 0 用容差 `abs(value) < 0.005`）。**不要用 `evaluate_story_autotext_values`**——它只涵蓋 storyArea，評本分類會回空且不報錯。
- 求值欄位數應該剛好等於「散裝顆數＋組合數」，多出來就是有填充重複掛在散裝與組合（見第二步的坑）。

## 第四步：產表

### 預設版式（使用者沒指定格式時）

兩欄：上半段「量」逐列列出（每列一顆 token），下半段「檢討」逐式列出。以垂直綠化設施面積檢討（GA≧(A-SGA)/2、SA≧GA/2）為例：

```
row 0   ◯◯檢討                                  （標題，跨兩欄合併、textbold、textsize 1）
row 1   規定               GA≧(A-SGA)/2 \n SA≧GA/2   （檢討方式原文，純文字）
row 2   GA：綠化面積        {token GA} m²          （單顆＝散裝 token）
row 3   A：垂直綠化設施面積  {token A} m²
row 4   SGA：結構必需之環樑面積 {token SGA} m²
row 5   SA：降版面積        {token SA組合} m²       （多顆＝組合合計 token，不要寫 {=a+b+c}）
row 6   檢討                                     （區塊標題列，跨兩欄合併、textbold）
row 7   (1)GA≧(A-SGA)/2    {GA} m² ≧ ({A}-{SGA})/2 = {=roundn(({A}-{SGA})/2, 2)} m²
row 8   (2)SA≧GA/2         {SA} m² ≧ {GA}/2 = {=roundn({GA}/2, 2)} m²
```

比例式的檢討（「某面積 ÷ 另一面積 ≧ 10%」）就把檢討列寫成 `{=roundn({A}/{B}*100, 2)} % ≧ 10%`。只有在**真的沒有對應組合**時（組合尚未建、或要臨時加減跨組的量）才用 `{=...}` 湊合計。

檢討列的「≧ 規定值」用**純文字**寫使用者提供的規定值；**結論（符合／不符合）用判斷式**寫成 `{?{A}/{B}*100 >= 10|符合|不符合}`（規則見下節），由外掛依當下數值判定、隨模型變動自動更新，**不要寫死**。判斷式需**外掛 ≥ 0.0.23**（以 `../table/references/mcp-compat.md` 為準）；外掛太舊時退回舊做法——結論預設不寫，使用者堅持要結論文字時可寫入當下判定，但回報時**必須**提醒「此結論為建表當下的判定，模型變動後不會自動改變，請以左式數值為準」。

### `{=...}` 公式規則（本表的核心能力）

- 文字中可穿插 `{=運算式}` 片段，一格可多段；**整格純公式可直接以 `=` 開頭**。
- 支援 `+ - * /` 與括號、`min(a,b)`／`max(a,b)`（門檻取大取小直接用它，不必拆兩支算式）、數值條件 `if(條件, 值A, 值B)`（級距、超過部分另計；兩值只能是數字，文字結論用判斷式）；進位函式 `roundn(x,n)`＝四捨五入、`ceiln(x,n)`＝無條件進位、`floorn(x,n)`＝無條件捨去（n＝小數位數）。**未包函式時預設四捨五入 2 位顯示**；法規對進位方式有規定時（如「無條件捨去至小數第二位」）務必用對函式。
- **函式用法**（面板鍵盤有 `min(`／`max(`／`if(` 鈕，MCP 直接寫）：
  - `min(a, b)`／`max(a, b)` 取小／取大（可多個參數），用在「不得超過」「不得低於」的上下限：
    `{=roundn(max(({A0}-{Ap})*(1-min({r},0.85)), 0.15*{A0}), 2)}` 一條同時處理「r 超過 0.85 以 0.85 計」與「A' 不得低於 0.15×A0」。
  - `if(條件, 成立值, 不成立值)` 是**數值**分段：條件須為比較式（`> >= < <= = !=`，可用 `and`／`or` 串接、前後留空白），兩值只能是數字或算式，可巢狀做級距：
    `{=roundn(if({A}>{X}, ({A}-{X})*0.5, 0), 2)}`（超過部分另計）、`{=if({A}<=500, 60, if({A}<=1000, 55, 50))}`（三段級距）。結果再套公式的進位規則。
  - 選擇原則：純上下限用 `min`／`max`、數值分段用 `if`、要輸出文字（符合／不符合）才用 `{?判斷式}`；`{?}` 的分支裡可放含 `if` 的公式，公式裡不能放 `{?}`。
- 運算元只能是**數字與數值類 autotext**（面積／數量／比率）：`%` 自動轉小數（`60.00%`→`0.6`）、千分位與 `m²` 自動剝除；文字類 token 代入不會計算。
- 放置到圖面與「更新自動文字」時自動重算；除零或語法錯誤該格顯示 `[公式錯誤]`。
- 公式裡嵌 autotext 的 segments 寫法（運算符與函式是文字、token 是 autotext 段，穿插組出）：
  ```json
  {"row": 4, "col": 1, "newline": 1, "segments": [
    {"type": "text", "value": "{=roundn(("},
    {"type": "autotext", "token": "${TJL$...A1}"},
    {"type": "text", "value": "+"},
    {"type": "autotext", "token": "${TJL$...A2}"},
    {"type": "text", "value": ")/"},
    {"type": "autotext", "token": "${TJL$...B1}"},
    {"type": "text", "value": "*100, 2)} %"}
  ]}
  ```

### `{?...}` 判斷式規則（外掛 ≥ 0.0.23）

- 語法 `{?條件|成立時內容|不成立時內容}`，可與文字、公式穿插，一格可多段；第二個 `|` 可省略＝不成立時顯示空白。
- **條件**是數值比較，運算元規則同公式（數字與數值類 token；`%` 自動轉小數）：支援 `> >= < <= = !=`、`and`／`or`（前後要留空白）、四則與括號、`min`／`max`；相等比較先 `roundn` 再比，避免浮點誤差。條件裡**不要**再包 `{=}`——條件本身就是運算式，直接寫算式即可。
- **成立／不成立內容**是任意文字，可放任何類別的 token，也可放 `{=公式}`（例：成立時顯示算出的值）。內容裡不能出現 `|`。
- 放置與「更新自動文字」時由外掛重算；條件算不出（文字 token 代入、除零、語法錯）該格顯示 `[判斷式錯誤]`。
- 典型用途：符合／不符合結論、「■ 合格 □ 不合格」勾選（兩個分支各寫一種勾法）。純數值的取大取小用公式的 `max`／`min`、數值分段用 `if()` 就好，不必動用判斷式。
- segments 寫法同公式（`{?`、比較符、`|` 是文字段，token 是 autotext 段）：
  ```json
  {"row": 7, "col": 2, "newline": 1, "segments": [
    {"type": "text", "value": "{?"},
    {"type": "autotext", "token": "${TJL$...A}"},
    {"type": "text", "value": "/"},
    {"type": "autotext", "token": "${TJL$...B}"},
    {"type": "text", "value": "*100 >= 10|符合|不符合}"}
  ]}
  ```
- 舊版外掛（< 0.0.23）會把 `{?…}` 當純文字原樣顯示：建表前看 `check_connection` 回報的外掛版本，太舊就退回「結論不寫死」。

### 建表流程（共通眉角見 `../table/references/spoke-conventions.md` 第 5～6 節）

1. **組 cells**：標題列 `textbold: true`、`textsize: 1`；區塊標題列 `textbold: true`；每格明確給 `newline`（未給時 `charwidth` 預設 1 會非預期縮減字寬）；區域名稱列左欄靠左、面積欄靠左。
2. `bimteki:create_project_table_template` 一次帶齊：`cells`、`merges`（標題與各區塊標題跨兩欄；**合併只能用 merges 參數**）、`equal_col=[0,0]`（放開內容欄等寬；不要傳空陣列）。取回傳 `nodeGuid`。
3. `bimteki:modify_project_table_template` 補樣板層級屬性：`template_name`（預設用檢討名稱，如「宜居建築垂直綠化檢討」；同名樣板已存在加日期後綴）、`table_type="normal"`、`column_widths`（如 `[240, 660]`）。
4. **驗證**：`bimteki:get_project_table_templates(template_guid=新guid)` 讀回，核對：列數與區塊結構、每顆散裝區域與每個組合的 token 都在（以 `originaldata` 含 token 為準；`statedata` 未評估屬正常）、**沒有殘留失效的舊 token**、公式片段完整（括號成對、函式名正確）、判斷式三段齊全（`{?條件|成立|不成立}`）、規定值未被誤植。
5. **數值 sanity check**：用 `evaluate_autotext_values(category="customAreaReview")` 取各區域／組合面積，手動照檢討方式算一次，確認與公式邏輯一致（公式本身要放置到圖面才會算出值）。注意 token 顯示值是四捨五入 2 位，與使用者手算稿差 0.01 很常見（實測值卡在進位邊界），**以模型值為準並主動說明差異來源**。
6. **回報**：樣板名稱；檢討項目與其散裝區域／區域組合清單（名稱＋面積＋組合成員數＋面積來源）；比例算式與規定值的來源（使用者提供）；提醒可在 **BIMTeki 表格管理器**放置到圖面（放置後公式才會算出實際值），以及主選單「**自訂面積項目檢討**」可隨時檢視／調整這些項目。
   - 表格已放置時，`modify_project_table_template` 會回 `placedTableCount`／`updatedPlacedTables`——確認有同步更新再回報。

## 常見案例：土管綠化面積檢討

土管（土地使用分區管制要點）的綠化率與喬木株數檢討沒有專屬 skill，用本流程做；外掛開檔時會把舊版綠化檢討工具的資料自動轉成**同一套結構**，所以命名固定、不要自創：

- **先把關**：只有都市計畫內（有土管）或特殊條例要求才須做；非都市土地且無條例要求就直接回報免檢討、不建表。規定值（基準是實設空地或法定空地、應綠化比率、綠化困難認定、喬木密度）**讀本案土管**，不憑記憶。
- **項目**「綠化面積檢討」；**組合**「實設綠化面積」（實際留設的綠化區域／填充）、「無法綠化面積」（土管認定的綠化困難部位，沒有就不建）。先 `get_project_custom_area_review` 看有沒有現成的（舊檔轉換或先前建過）→ 沿用。
- **自訂義參數**（分類「綠化面積檢討」，`set_project_custom_params` upsert，值先給使用者確認）：「綠化比率」`50%`（帶 % 號，代入公式自動 ÷100）、「喬木檢討基準」`64`（每滿多少 m² 一株）、「實設喬木數量」`3`（純數字，**不帶「棵」**）、「檢討基數」`實設空地`／`法定空地`（純標籤）。token 用 `get_project_autotext_catalog(category="customParam")` 比對 display。
- **基準空地**：實設空地＝`category="coverage"` 的「面積：使用面積(建蔽率用)總計」`{U}` 減「面積：設計建築面積」`{D}`；法定空地＝`category="siteOverview"` 的「面積：法定空地面積」`{L}`（另有「計算式：法定空地面積計算式」）。
- **三個運算式**（`{G實}`／`{G無}`＝組合合計 token，`{P率}`／`{P基}`／`{P株}`／`{P名}`＝參數 token）：

  ```
  E ＝ {U}-{D}（法定空地基準時 ＝ {L}；進乘除時包括號）
  S ＝ (E-{G無})*{P率}（沒有無法綠化組合時 ＝ E*{P率}）
  T ＝ floorn(roundn(E/{P基},2),0)（應植棵數：先四捨五入 2 位再無條件捨去）
  ```

- **兩欄六列**（左欄標籤用本案土管用詞）：標題「綠化面積檢討」（跨兩欄）→ 實設／法定空地面積 `{U}-{D}={=E}m²`（法定基準用計算式 token）→ 綠化面積 `{G實式}`（組合 `formulaToken`）→〔有組合才放〕綠化有困難面積 `{G無式名}`（`formulaWithZoneNameToken`）→ 應綠化面積 `(E-{G無})*{P率}={=S}m²` → 檢討 `{G實}{?{G實}>=S|≧|<}{=S}{?{G實}>=S|符合規定...OK！|...請重新檢討！}` → 喬木數量檢討 `{P名}面積 E/{P基}={=roundn(E/{P基},2)}...取{=T}棵。實設喬木數量：{P株}棵 {?{P株}>=T|≧|<}{=T}，{?{P株}>=T|符合規定...OK!|請重新檢討!}`。
- **判斷式條件內不能放 `{=`**：條件裡的 S、T 要展開成運算式，分支內才用 `{=S}`／`{=T}`。版本需求（外掛 ≥ 0.0.23、MCP ≥ 0.13.0）見 `../table/references/mcp-compat.md`；工具清單裡還有 `get_project_green_info` 代表外掛太舊，請使用者升級，不要退回舊流程。

## 注意事項

- **token 綁項目／區域／組合 GUID**：三者改名都不影響已放置的 token；但 `delete_item`／`remove_zones`／`clear_zones`／`delete_group` 會讓受影響區域或組合已放置的自動文字**變成空字串**——執行這四種動作前先提醒使用者。搬項目、換掛法也會換 token（見第三步）。
- 區域面積由元素觀察者自動同步：使用者改了圖面，項目內面積、組合合計與已放置的 token 都會跟著更新，不需要重建表。
- 掛錯了（選錯元素）用 `remove_zones`（散裝單顆）、`clear_zones`（整批散裝重來）、`remove_zones_from_group`／`delete_group`（組合）修正，再重新掛。
- 檢討項目屬專案資料，會存進 `.bteki`；同名項目 MCP 端會擋（名稱定位需唯一），跨呼叫定位優先用 `itemId`；組合名稱在同一項目內也需唯一，定位優先用 `groupId`。
- 規定值、判定方向屬法規事實，一律以使用者提供為準；不確定就問，不要臆測、不要寫死臆測的結論。
- 新建樣板與匯入都會寫入專案並存檔，屬可逆性低操作；刪除既有項目或樣板須先取得使用者明確同意。
