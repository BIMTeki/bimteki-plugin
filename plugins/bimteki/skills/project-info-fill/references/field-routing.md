# 欄位分流表：內建欄位 → 專屬工具 → 自訂義參數

判斷每筆擷取到的資料該用哪個工具。優先序：**內建欄位（`set_project_core_info`）→ 各領域專屬 `set_*` 工具 → 都沒有才走 `set_project_custom_params`。**

---

## A. `set_project_core_info` 可寫欄位（內建，優先用）

欄位名鏡射 `get_project_core_snapshot`。partial update，只放要改的鍵。任一欄位不合法會**整批**退回。
**四個頂層鍵**：`site`、`building`、`review_settings`、`cost`，至少提供其一。

### `site`（基地概要）

| 鍵 | 型別 | 說明 |
|---|---|---|
| `in_urban_area` | bool | 位於都市計畫區 |
| `urban_plan_name` | str | 都市計畫名稱（空字串＝清空）。**「都市計畫名稱」走這裡，不要寫成自訂義參數。** |
| `front_roads` | list[str] | 面前道路；整組替換，`[]` 清空 |

### `building`（建築概要）

| 鍵 | 型別 | 說明 |
|---|---|---|
| `owner` | str | 起造人 |
| `building_count` | int ≥ 0 | 幢數 |
| `usage_classes` | list[str] | 建築使用用途；整組替換。每筆**優先用類組代碼**（如 `"H-2"`、`"G-2"`），其次精確類組名稱，其他文字存為自訂項 |
| `has_shelter` | bool | 是否設置防空避難室 |
| `excavation_rate` | number 0~100 | 開挖率（百分比數值，`55.5`＝55.5%） |
| `height_ratio` | number ≥ 0 | 高度比 |
| `setback_rule` | str | 退縮規定 |
| `building_height` | number > 0 | 建築高度（公尺）。寫入即轉「自訂」，不再隨樓層自動推導；未同時給 `eave_height` 時簷高連動＝建築高度−0.15 |
| `eave_height` | number > 0 | 簷高（公尺）。寫入即轉「自訂」 |
| `is_public_building` | bool | 供公眾使用建築物 |
| `has_rainwater_pond` | bool | 雨水滯洪池 |
| `mechanic_ratio` | number | 機電檢討。**只有 10% 與 15% 兩種**：傳 `10` 或 `15`（百分比數值），亦接受 `0.1`／`0.15`。**變更會觸發全案重算** |

### `review_settings`（容積檢討設定；**變更會觸發全案檢討重算，只在使用者明確要求時才寫**）

| 鍵 | 型別 | 說明 |
|---|---|---|
| `basement_review_mode` | str | `"sum"`=地下層總量檢討／`"per_story"`=分層檢討 |
| `roof_review_per_block` | bool | 各棟檢討屋突面積 |
| `arcade_in_arch_for_roof` | bool | 騎樓同建築面積計入屋突層計算 |
| `arcade_in_arch_for_shelter` | bool | 騎樓同建築面積計入防空避難室計算 |
| `balcony_in_floor_area` | bool | 工廠類建築（陽台全額計入容積樓地板面積計算） |
| `minus_arcade_from_site` | bool | 建蔽率計算時騎樓地從基地母數扣除 |
| `car_minus_void` / `scooter_minus_void` / `bike_minus_void` | number ≥ 0 | 汽／機／自行車每輛可扣容積（m²） |
| `rounding_rule` | str | `"round"`=四捨五入／`"floor"`=無條件捨去（皆至小數點後 2 位）。舊檔可能存有 `"ceil"`／`"none"`，**讀得到但不可寫回** |
| `area_source` | str | `"original"`=區域原始面積／`"overwrite"`=覆寫面積。**會改變所有區域的取值來源並觸發全案重算** |

（`auto_renew_zone` 刻意不開放——那是使用者對「BIMTeki 何時可以自動動我的資料」的偏好，請他自己在面板改。）

### `cost`（工程造價；只收使用者輸入，金額由系統算出）

| 鍵 | 型別 | 說明 |
|---|---|---|
| `unit_price` | number > 0 | 工程造價標準（單價）。依當年度地方主管機關公告，屬外部資訊 → 抓不到就問使用者 |
| `fencing_formula` | str | 雜項工作物造價的「輸入計算式」（例 `"1200*35"`）；金額由系統求值 |
| `building_rounding` / `fencing_rounding` | obj | `{"digits": 1~10, "rule": "round"\|"floor"\|"ceil"\|"none"}` |

**建築工程造價／雜項工作物造價／總工程造價的「金額」是計算結果，不可寫入。**

回傳：`changed`、`warnings`、`savedToFile`。

### 寫入陷阱

- **整批驗證**：可疑欄位不要跟有把握的混在一起送；必要時分兩次 `set_project_core_info`。
- `building_height`／`eave_height` 一旦寫入就打斷自動推導，非必要別動。
- `usage_classes`、`front_roads` 是「整組替換」，不是追加；要先把既有值一起帶上再加新的。
- `review_settings` 與 `mechanic_ratio` 會觸發全案重算，**不要順手帶**。

---

## B. 有專屬寫入工具的資料（`set_project_core_info` 管不到，但可寫）

| 資料 | 工具 | 參數重點 | 前提／陷阱 |
|---|---|---|---|
| 土地地號（地段／地號／面積） | `set_project_land_info` | `parcels`：每筆 `{zone_usage, section_name, parcel_number, area_m2}` | **整批覆寫**。覆寫時依 `zone_usage` 沿用舊的扣除項；只有被移除的分區其扣除項才會消失（回 warning）。**「地號只能在面板改」已不成立** |
| 容積獎勵 | `set_project_land_info` | `bonus_items`：`{name, type:"normal"\|"special", …}`，`[]` 清空 | 整批取代 |
| 保留地／道路退縮地／道路退縮地(計入法空)／鄰房侵占面積 | `set_land_deduction_areas` | `parcels`：每筆 `{zone_usage, reserved_area, road_reserved_area, road_reserved_empty_area, neighbor_reserved_area}`，至少給四者其一 | **只在「扣除項使用者自訂」模式可用**（snapshot 的 `land.is_user_define_reserved_area` 為 true 且各 `deductions.writable` 為 true）。預設「由區域推導」模式會直接拒絕，**且不代為切換**。騎樓面積／騎樓樓地面積兩模式下都由建築面積區域重建，純計算值不可寫 |
| 各棟各層戶數／樓高／用途 | `set_story_attributes` | `stories`：每筆 `{storyGuid, familyCount, floorHeight, purpose}`，至少給三者其一 | `storyGuid` 取自 `get_project_stories`。**該欄位 `isCustom` 為 true 才寫得進去**，否則重算會壓回 `original`；總計層的樓高／用途永遠不可寫。**`floorHeight` 單位是公分**（320＝3.2 公尺）。樓層骨架（名稱／夾層／排序）無工具可改 |
| 法定汽／機／自行車位數 | `set_legal_parking_counts` | `legal_car_count` / `legal_motorcycle_count` / `legal_bicycle_count` | partial update。**`-1`＝清除（顯示「－」）、`0`＝檢討結論為免設**，意義不同別搞混 |
| 停車檢討的設定與敘述 | `set_project_parking_review` | `law_type`（`"building_code"`／`"land_use_control"`）、`category_type`（`"single"`／`"multi"`）、`custom_law_content`、`result_content`、`is_detail_setting`、`auto_fill_legal_counts` | 實設位數與地下層逐層明細由停車區域推導，**不可寫** |
| 棟別／戶別清單 | `set_bimteki_block_unit_settings` | `blocks`／`units` 各可含 `add`／`rename`／`delete` | 棟別增刪僅限多棟案型；改名／刪除會連動遷移既有區域與樓梯座綁定 |

對應的讀取工具：`get_project_core_snapshot`（土地與扣除項）、`get_project_stories`、`get_project_parking_info`、`get_bimteki_block_unit_settings`。**寫入前一律先讀現況做 read-modify-write。**

---

## B-2. 純計算結果與刻意不開放（**不可寫，寫了整批退回**）

- **純計算結果**（由模型／區域／上面那些輸入推導）：基地面積、使用面積、棟數、樓層數、開挖面積，整個 `land` 的基準/設計建蔽率、容積率、允建容積樓地板面積，工程造價的三個「金額」，停車實設位數與地下層明細，綠化面積（由「自訂面積項目檢討」項目「綠化面積檢討」的區域組合推導）。→ 要改請改**輸入**或改**模型/區域**。
- **刻意不開放**：`building.case_type`／`block_mode`／`shared_hall`（改案型會重塑整個檢討結構）、`review_settings.auto_renew_zone`。→ 請使用者自己在面板決定。
- 使用分區（`site.zone`）由土地地號資料推導 → 改地號用 `set_project_land_info`。

若只是想留存法定值當外部依據（例如「法定建蔽率50%／容積率140%」），改寫成自訂義參數，並在回報中註明「此為外部依據，非 BIMTeki 計算值」。

---

## C. `set_project_custom_params`（前兩類都沒有對應欄位時，寫成自訂義參數）

`params` 每筆依 `action` 而定（省略＝`upsert`）：

- **upsert**：`{"category","name","content"}` — 同名已存在只覆寫 content、不搬分類；分類自動建立。
- **delete**：`{"action":"delete","name":項目名稱}`。
- **rename**：`{"action":"rename","name":舊名稱,"new_name":新名稱}` — 新名稱不可與其他既有項目同名。

`name` 全案唯一，成為 autotext 欄位鍵 `CustomParam.{name}`；任一筆不合法整批退回。

> ⚠ 該鍵綁的是**項目名稱**：改分類名稱或搬分類不影響它，但 **delete／rename 會讓原本綁舊名的表格樣板失效**，回傳 `warnings` 會列出受影響的鍵 → 先問過使用者，事後主動告知哪些表格要改綁。

### 命名：**優先沿用專案既有的自訂義參數名稱**

**動手前務必先 `get_project_custom_params`，把既有的分類→項目樹（`name`／`content`／`fieldKey`）抄下來**（`get_project_autotext_catalog(category="customParam")` 也看得到，但前者直接給 `fieldKey`，更適合做 read-modify-write）。
若專案已有語意相同的項目 → **用完全相同的項目名**，讓 `set_project_custom_params` 走 upsert（只覆寫 content），檢討表原本綁的 token 不會斷。**不要**自創近義新名（如既有「地質敏感區判定」就別再新增「地質敏感地區」），否則會產生兩個 token、表格綁到空的那個。

事務所常用的既有慣例是分類 **「建照審查資料」** 底下這批項目名（實測自專案 catalog，供對照；以目標專案實際 catalog 為準）：

| 分類 category | 項目 name（→token `CustomParam.{name}`） | 內容 content 範例 | 主要供哪張檢討表用 |
|---|---|---|---|
| 建照審查資料 | `地質敏感區判定` | `位於地下水補注地質敏感區（非山坡地）` | 建照審查第21項 |
| 建照審查資料 | `地質技師公會核定函` | （逐字函號＋日期，抓不到留空待人工填） | 建照審查第21項 |
| 建照審查資料 | `軍事禁限建判定` | `位於軍事禁限建地區，高度150M以下免會辦軍方` | 建照審查第20項 |
| 建照審查資料 | `建築線判定` | `位於免指定建築線範圍` 或逐字指定文號 | 建照審查第19項 |
| 建照審查資料 | `都市計畫核准函` | （府都計字第◯號＋日期，抓不到留空） | 建照審查第24項 |
| 建照審查資料 | `細部計畫開發方式` | （逐字，抓不到留空） | 建照審查/土管 |
| 建照審查資料 | `建築物用途組別` | `G-2辦公室、H-2集合住宅` | 建照審查第26項 |
| 建照審查資料 | `建築物高度含屋突` | （逐字，含屋突高度） | 高度檢討 |
| 建照審查資料 | `高度檢討圖號` | `A0-◯`（圖號） | 建照審查第23項 |
| 建照審查資料 | `畸零地基地寬度` | （逐字，抓不到留空） | 建照審查第19項 |
| 建照審查資料 | `畸零地基地深度` | （逐字，抓不到留空） | 建照審查第19項 |
| 建照審查資料 | `畸零地檢討圖號` | `A0-◯` | 建照審查第19項 |

**綠化規定值的固定命名**（綠化面積檢討表的公式與外掛的舊檔轉換都綁這幾個名字，一律照用、不要改名）：

| 分類 category | 項目 name | 內容 content 寫法 | 供哪張表用 |
|---|---|---|---|
| 綠化面積檢討 | `綠化比率` | `50%`（帶 % 號，公式代入自動 ÷100） | 綠化面積檢討表 |
| 綠化面積檢討 | `喬木檢討基準` | `64`（每滿多少 m² 植喬木一株，純數字） | 綠化面積檢討表 |
| 綠化面積檢討 | `實設喬木數量` | `3`（純數字，不帶「棵」） | 綠化面積檢討表 |
| 綠化面積檢討 | `檢討基數` | `實設空地` 或 `法定空地`（純標籤） | 綠化面積檢討表 |

綠化面積本身不是參數：由「自訂面積項目檢討」項目「綠化面積檢討」的組合「實設綠化面積」「無法綠化面積」推導，要改請改區域（表以 `custom-area-review` 的一般流程建）。

**沒有對應既有項目時**才新增；新增時沿用同一套風格（優先放「建照審查資料」等既有分類，項目名用「◯◯判定／◯◯函／◯◯圖號」句式）。其他常見需求若專案尚無項目，可參考：`都市計畫發布文號`、`都市計畫發布日期`、`細部計畫名稱`、`整體性防火間隔判定`、`排水污水放流函`、`宜居回饋金`、`法定建蔽率`／`法定容積率`（後兩者為外部依據，非 BIMTeki 計算值，回報時註明）。

> 內容一律逐字照抄來源文件；抓不到就留空字串並列入「待人工確認」，**絕不臆測**。

---

## D. 分流決策速查

1. 是「都市計畫名稱」「面前道路」「起造人」「建築高度/簷高」「退縮規定」「開挖率」「防空避難室」「供公眾使用」「雨水滯洪池」「幢數」「建築使用用途」「機電檢討10/15%」「容積檢討設定」「工程造價單價/雜項算式」？ → **A（內建 `set_project_core_info`，四個頂層鍵）**
2. 是「地號/土地面積」「容積獎勵」「保留地/道路退縮地/鄰房侵占」「各層戶數/樓高/用途」「法定車位數」「停車檢討設定」「綠化比率/喬木」「棟別戶別清單」？ → **B（各領域專屬 `set_*`，注意前提條件）**
3. 是「基地面積/使用面積/建蔽率/容積率/樓層數/造價金額/實設車位/綠化面積」等計算結果，或「案型/共用梯廳/單多棟/auto_renew_zone」？ → **B-2（不寫；要留存改走 C 並註明外部依據）**
4. 其他檢討表要用但 BIMTeki 沒有任何對應欄位（地質敏感、各類函號/日期、細部計畫、宜居回饋金…）？ → **C（自訂義參數 `set_project_custom_params`）**
