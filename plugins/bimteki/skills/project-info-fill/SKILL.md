---
name: project-info-fill
description: >-
  把「專案資料夾」裡的建築/土地資料回填到 BIMTeki 專案（寫回專案資訊面板的內建欄位、各領域專屬設定，並把沒有對應欄位、但檢討表會用到的資料寫成「使用者自訂義參數」）。當使用者想要「把資料填回 BIMTeki / 回填專案資訊 / 寫回專案資訊 / 填寫 BIMTeki 專案資訊面板 / 把資料夾資料同步進 BIMTeki / 新增自訂義參數（例如地質敏感地區、都市計畫名稱與函文）/ backfill project info / fill BIMTeki project info」時務必使用本 skill，即使沒有明講「skill」二字。流程：先 check_connection、get_project_status（定案/未存檔把關）、get_project_core_snapshot 與 get_project_custom_params 讀現況，再依 references/source-map.md 從資料夾關鍵文件（概要表、土地使用分區、都市計畫書、地質敏感查詢、謄本、宜居/綠建築等）擷取值，接著依 references/field-routing.md 分流：內建欄位用 set_project_core_info（site/building/review_settings/cost 四個頂層鍵），有專屬工具者用 set_project_land_info / set_land_deduction_areas / set_story_attributes / set_legal_parking_counts / set_project_parking_review，都沒有才用 set_project_custom_params（upsert/delete/rename，項目名稱即 CustomParam.{name} 欄位鍵），最後讀回驗證並回報「已寫入 / 待人工確認」清單。本 skill 只負責「回填專案資訊與自訂義參數」；製作檢討表格、繪製容積區域、門窗檢討、法規查詢、面積總表另有各自的 skill，不要用本 skill 處理。
---

# BIMTeki 專案資訊回填（Project Info Backfill）

把專案資料夾裡零散在 PDF／DOCX 的建築、土地資料，整理後寫回 BIMTeki 專案，讓後續各種檢討表能直接引用 autotext，不用每張表重打一次。這件事的價值在「單一真實來源」：資料一旦回填進 BIMTeki，面積總表、建照審查表、土管表、無障礙表都能綁同一份專案資訊或自訂義參數，改一次全部同步。

本 skill 只做「寫回專案資訊」。實際建表交給各檢討表 skill。

## 核心觀念（先讀懂再動手）

BIMTeki 的專案資訊有**多條**寫入路徑，優先序很重要——先找「有沒有對應的專屬寫入工具」，最後才退到自訂義參數：

1. **專案資訊面板的內建欄位** → `set_project_core_info`。四個頂層鍵：`site`（基地概要）、`building`（建築概要）、`review_settings`（容積檢討設定）、`cost`（工程造價）。**有內建欄位的資料一律走這條**，因為它們會連動計算、並被既有 autotext（siteOverview／buildingOverview 等）引用。
2. **各領域的專屬寫入工具**（都是 `set_project_core_info` 管不到、但確實可寫的資料）：
   - `set_project_land_info` — 土地地號（地段/地號/面積，整批覆寫）與容積獎勵明細。
   - `set_land_deduction_areas` — 逐分區的保留地／道路退縮地／道路退縮地(計入法空)／鄰房侵占面積。**僅限「扣除項使用者自訂」模式**（見下）。
   - `set_story_attributes` — 各棟各層的戶數／樓高／用途。**僅限該欄位已切成自訂模式**（見下）。
   - `set_legal_parking_counts` — 法定汽／機／自行車位數；`set_project_parking_review` — 停車檢討的設定與敘述。
   - `set_bimteki_block_unit_settings` — 棟別／戶別清單（多棟才能增刪棟別）。
3. **以上都沒有對應欄位的資料** → `set_project_custom_params` 寫成「使用者自訂義參數」。每筆的「項目名稱」全案唯一，且**自動變成 autotext 欄位鍵 `CustomParam.{name}`**，檢討表可以直接綁它。使用者點名的「地質敏感地區」「都市計畫發布日期與函文」多屬此類。
   - **綠化規定值也走這條，且名稱固定**：分類「綠化面積檢討」→「綠化比率」（`50%`）、「喬木檢討基準」（`64`）、「實設喬木數量」（`3`）、「檢討基數」（`實設空地`／`法定空地`）。綠化面積檢討表的公式（`custom-area-review` 的土管綠化案例）綁這幾個名字，外掛的舊檔轉換也產生同名項目，不要自創近義名；細節見 `references/field-routing.md` C 節。

**所有 `set_*` 工具都會寫入專案並存檔（.bteki），且案件「已定案（finalized）」時會被拒絕。** 因此務必：讀現況 → 對照擷取值 → 只寫「有變更且合法」的欄位 → 讀回驗證。

**真正不可寫的是「純計算結果」**（寫了會整批退回）：基地面積、使用面積、棟數、樓層數、開挖面積、整個 `land` 的建蔽率／容積率／允建容積樓地板面積、工程造價的「金額」、停車實設位數、綠化各項面積。它們由模型與上面那些輸入推導出來——要改請改**輸入**或改**模型/區域**，不要試圖直接寫結果。

另有兩項是**刻意不開放**、不是單純唯讀：`building` 的 `case_type`／`block_mode`／`shared_hall`（改案型會重塑整個檢討結構，須由使用者在面板上決定），以及 `review_settings.auto_renew_zone`（這是使用者對「BIMTeki 何時可以自動動我的資料」的偏好）。這兩類一律請使用者自己在面板改。

## 流程

### 步驟 0：前置

- 這個 skill 會**修改使用者的 BIMTeki 專案並存檔**，屬於有副作用的操作。開始前先向使用者確認「要寫入目前開啟的這個 BIMTeki 專案」，並在寫入前把「即將寫入的欄位與值」列給使用者過目（見步驟 4 的預覽）。
- 確認資料夾路徑（通常就是目前工作的專案資料夾）。

### 步驟 1：連線並讀現況

依序呼叫：

1. `check_connection` — 確認 Archicad／BIMTeki Studio 可被呼叫。失敗就請使用者開啟 BIMTeki 專案後再試。
2. `get_project_status` — **一批寫入前的必做把關**（唯讀、成本低）：
   - `finalized` 為 true（建照定案／變更設計定案）→ **所有 `set_*` 都會被拒絕**。先告知使用者「本案已定案、無法寫入」，不要硬寫。
   - `project_file.hasFile` 為 false → 專案只存在記憶體中，寫入無法落地，請使用者先「另存新檔」再回來。
   - 另可看 `has_unsaved_changes` 與 `project_link`（與哪個 .pln 連結）。
3. `get_project_core_snapshot` — 取得 `site`／`building`／`review_settings`／`land` 現況。**這是判斷「哪些欄位已經有值、哪些空著、哪些不可寫」的依據**，也讓你之後只寫真正需要變更的欄位（partial update）。
   - 順手核對：目前開啟的專案是不是使用者要回填的那一案？比對 `site.site_address`、`site.urban_plan_name`、`building.owner` 與資料夾內文件。**若明顯不符（例如開的是範例／別案），立刻停下來問使用者**，不要把 A 案資料寫進 B 案。
   - 要動扣除項時，另看 `land.is_user_define_reserved_area` 與各 `land.parcels[].deductions` 的 `writable`（見步驟 5-2）。
4. `get_project_custom_params` — 讀出自訂義參數的完整分類→項目樹（每筆含 `name`／`content`／`fieldKey`）。**這是命名對齊的權威來源**：先看有沒有語意相同的既有項目，避免重複命名造成兩個 token。（`get_project_autotext_catalog` 也看得到，但這個工具直接給 `fieldKey`＝`CustomParam.{項目名}`，更適合做 read-modify-write。）
5. 要動戶數／樓高／用途時才呼叫 `get_project_stories`；要動棟別／戶別清單時才呼叫 `get_bimteki_block_unit_settings`。

### 步驟 2：從資料夾擷取值

依 `references/source-map.md` 找到並讀取關鍵文件，擷取每個目標欄位的值。重點：

- 政府 PDF 常是掃描或文字層亂碼；需要**逐字精確的函號、日期、都市計畫名稱**時，用視覺方式（PDF skill 轉圖或直接讀頁面）抄錄，不要靠可能亂碼的文字層。
- **逐字照抄**函號、日期、都市計畫書名稱；不要自行推算或美化。
- **抓不到就標記為待人工確認，絕不臆測**。寧可留白讓使用者補，也不要填一個看起來像但其實錯的函號。
- 數值欄位（高度、簷高、開挖率等）記得單位：公尺、百分比數值（55.5 表示 55.5%）。

### 步驟 3：分流每一筆資料（內建 vs 自訂義）

對照 `references/field-routing.md`，把步驟 2 擷取到的每筆資料歸類：

- 命中「內建可寫欄位」→ 併入 `set_project_core_info` 的 `site`／`building`／`review_settings`／`cost` 物件。
- 命中「有專屬寫入工具」→ 記到對應工具的批次（`set_project_land_info`／`set_land_deduction_areas`／`set_story_attributes`／`set_legal_parking_counts`／`set_project_parking_review`），並記下該工具的前提條件。
- 命中「純計算結果／刻意不開放」→ 不寫（若只是想留存外部依據，改走自訂義參數，並在回報中註明「此為外部依據，非 BIMTeki 計算值」）。
- 其餘（檢討表要用、但 BIMTeki 沒有任何對應欄位）→ 併入 `set_project_custom_params` 的 `params` 陣列，依 field-routing.md 建議的 `category`／`name`。

### 步驟 4：寫入前預覽並確認

把「內建欄位變更清單」與「自訂義參數清單」整理成表格列給使用者，標明每筆的值與來源文件，以及「待人工確認」的項目。取得使用者同意後再寫。這一步是防呆：寫入會存檔且案件可能被別人同時編輯。

### 步驟 5-1：寫入內建欄位 `set_project_core_info`

- **partial update**：只放要改的鍵，沒放的欄位不動。
- 四個頂層鍵 `site`、`building`、`review_settings`、`cost`，至少提供其一。可寫欄位與型別見 field-routing.md。
- `review_settings`（容積檢討設定）與 `building.mechanic_ratio`（機電檢討 10%／15%）**變更會觸發全案重算**；`review_settings.area_source` 更會改變所有區域的取值來源。這類欄位不要順手帶，**只在使用者明確要求時才寫**。
- `usage_classes`：整組替換的 list。**每筆優先用類組代碼**（如 `"H-2"`、`"G-2"`），其次精確類組名稱，其他文字會存成自訂項。
- `front_roads`：整組替換的 list[str]；`[]` 代表清空。
- `building_height`／`eave_height`：一旦寫入就轉成「自訂」不再隨樓層自動推導；只寫 `building_height` 而未給 `eave_height` 時，簷高會連動為 建築高度−0.15。**除非確有需要，否則別亂動這兩個**，以免打斷自動推導。
- **整批驗證**：任一欄位不合法（含未知／唯讀欄位）會導致**整批不寫入**並回傳 `errors`。所以寧可分兩次呼叫（先把有把握的寫進去），也不要把一個可疑欄位混進去害整批失敗。
- 回傳會給 `changed`（實際變更欄位）、`warnings`、`savedToFile`；記錄下來。

### 步驟 5-2：寫入有專屬工具的欄位

只在這批資料真的有擷取到、且使用者同意時才做。每個工具都有前提條件，**不符合就停下來告知使用者，不要繞路硬寫**：

| 資料 | 工具 | 前提與眉角 |
|---|---|---|
| 土地地號（地段／地號／面積）、容積獎勵 | `set_project_land_info` | `parcels` / `bonus_items` 各為**整批覆寫**，`[]` 代表清空。覆寫 parcels 時會依 `zone_usage` 沿用舊的扣除項；只有被移除的分區，其扣除項才會一併消失（回傳 warning）。 |
| 保留地／道路退縮地／道路退縮地(計入法空)／鄰房侵占 | `set_land_deduction_areas` | **只在「扣除項使用者自訂」模式可用**（`land.is_user_define_reserved_area` 為 true 且各 `deductions.writable` 為 true）。預設的「由區域推導」模式下每次重算都會清空重建，工具會直接拒絕，**而且不會代為切換模式**——必須請使用者自己到土地資訊設定切換。騎樓面積／騎樓樓地面積兩種模式下都是純計算值，不可寫。 |
| 各棟各層戶數／樓高／用途 | `set_story_attributes` | 每筆要 `storyGuid`（取自 `get_project_stories`）。**欄位只有在 `isCustom` 為 true 時才寫得進去**，否則每次重算都會被壓回 `original`；總計層的樓高／用途永遠不可寫。`floorHeight` 單位是**公分**（320＝3.2 公尺）。樓層骨架本身（名稱、夾層、排序）沒有任何工具可以改。 |
| 法定汽／機／自行車位數 | `set_legal_parking_counts` | partial update；`-1`＝清除（面板顯示「－」），`0`＝檢討結論為免設，兩者意義不同。 |
| 停車檢討設定與敘述 | `set_project_parking_review` | 只收設定（law_type／category_type／自訂法規內容／檢討結果敘述等）；**實設位數與地下層明細由停車區域推導，不可寫**。 |
| 棟別／戶別清單 | `set_bimteki_block_unit_settings` | 棟別增刪僅限多棟案型；改名／刪除會連動遷移既有區域。 |

寫完各自讀回（對應的 `get_*`）確認，並把 `changed`／`warnings`／`savedToFile` 記下來。

### 步驟 6：寫入自訂義參數 `set_project_custom_params`

- 每筆依 `action` 而定（省略＝`upsert`）：
  - **upsert**：`{"category": 分類, "name": 項目名稱, "content": 內容}`（content 可為空字串）。同名已存在 → 只覆寫 content、不搬分類；分類不存在會自動建立。
  - **delete**：`{"action": "delete", "name": 項目名稱}`。
  - **rename**：`{"action": "rename", "name": 舊名稱, "new_name": 新名稱}`；新名稱不可與其他既有項目同名。
- **項目名稱全案唯一**，且成為 autotext 欄位鍵 `CustomParam.{name}`。命名要穩定、可讀、可被檢討表引用（例：`地質敏感地區`、`都市計畫發布文號`）。
- ⚠ **這個鍵綁的是「項目名稱」**：改分類名稱或搬分類都不影響它，但 **`delete` 與 `rename` 會讓原本綁舊名的表格樣板失效**。回傳的 `warnings` 會列出受影響的鍵——**務必主動告知使用者哪些表格要改綁**。因此 delete／rename 前先問過使用者，不要為了「整理命名」自作主張改名。
- 任一筆格式不合法 → 整批不寫入並回傳 `errors`。
- 回傳每筆 `name／action（created|updated|deleted|renamed）／category`、`warnings` 與 `savedToFile`；記錄下來。

### 步驟 7：讀回驗證並回報

- 再次 `get_project_core_snapshot`，確認內建欄位已變成預期值（比對 `text`）。
- 有用到專屬工具的，各自讀回對應的 `get_*`（`get_project_stories`／`get_project_parking_info`／土地與扣除項看 snapshot 的 `land`）。
- `get_project_custom_params`，確認新增／更新的自訂義參數項目都在、`fieldKey` 為 `CustomParam.{name}`。
- 向使用者回報四塊：
  1. **已寫入內建欄位**（欄位→新值→來源）。
  2. **已用專屬工具寫入的項目**（工具→欄位→新值→來源）。
  3. **已寫入自訂義參數**（分類／項目→內容→token→來源）；若有 delete／rename，**額外列出受影響、需要改綁的表格樣板**。
  4. **待人工確認清單**：抓不到、或需外部函號／日期、或屬純計算結果／刻意不開放而無法寫、或因前提條件不符（扣除項非自訂模式、樓層欄位非自訂模式）而略過、或案件已定案而略過者，逐條列出並說明原因與建議補法。

## 注意事項

- **絕不臆測**函號、日期、地號、分區。抓不到就留待人工確認。
- **不要試圖寫純計算結果**（面積、比率、造價金額、實設車位…）；要改請改輸入或改模型/區域。
- **有專屬寫入路徑者優先用專屬工具**（內建欄位 → `set_project_core_info`，其次各領域 `set_*`），不要為了省事全部塞進自訂義參數（那樣會失去連動與既有 autotext 綁定）。
- **前提條件不符時不要繞路**：扣除項要「使用者自訂」模式、樓層欄位要 `isCustom`——這兩者本 skill **不代為切換**，一律請使用者自己在面板改，否則寫進去會被下次重算清掉。
- **會觸發全案重算的欄位**（`review_settings.*`、`building.mechanic_ratio`、`area_source`）只在使用者明確要求時才寫。
- **自訂義參數的 delete／rename 會打斷表格綁定**，先問過使用者，並在回報中列出要改綁的樣板。
- 寫入前務必預覽、寫入後務必讀回驗證；工具會存檔，錯了要人工回復很麻煩。
- 本 skill 不建表、不畫容積、不查法規。需要那些請改用對應 skill。

## 參考檔

- `references/source-map.md` — 資料夾文件 → 欄位對照（哪個檔找哪個值）。
- `references/field-routing.md` — 每個目標欄位 → 內建欄位鍵或自訂義參數建議，含唯讀欄位清單與型別、寫入注意。
