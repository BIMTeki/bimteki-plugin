---
name: table-area
argument-hint: "[全部|面積總表|容積|地下|屋突|建蔽|基地|清單]"
description: BIMTeki「面積與容積檢討表」入口：以外掛的一鍵生成工具 `generate_area_review_tables` 產出六張表的樣板（各層樓地板面積總表、各層容積檢討、地下層容積檢討、屋突面積檢討、建蔽率檢討、基地概要），所有數值綁 autotext、重跑原地更新。當使用者想要「做面積表 / 做面積總表 / 做容積檢討 / 做地下層容積檢討 / 做屋突檢討 / 做建蔽率檢討 / 做基地概要 / 一鍵生成容積檢討表 / 這些面積容積的表可以做哪些 / area and volume review tables」時務必使用本 skill，即使沒有明講「skill」二字。可帶關鍵字指定只做哪幾張。**先決條件：容積區域與建築面積區域已繪製並匯入 BIMTeki**，工具會自行判斷並在回傳裡說明略過原因，本 skill 不代畫區域。本 skill 不手動組 cells、也沒有手建退路：外掛早於 v1.1.0 就請使用者更新。法規條文類（建照審查表、土管、無障礙）是另一個 hub `table-code`，不在本 skill 範圍。
---

# BIMTeki 面積與容積檢討表（一鍵生成入口）

六張面積／容積檢討表的版面、案型分支、0 值過濾與 token 綁定**全部由外掛決定**（`generate_area_review_tables`），本 skill 只負責：確認前提、跟使用者確認要建哪幾張、呼叫工具、把回傳講清楚、處理工具做不到的例外。**不要再用 `create_project_table_template` 一格一格手建這六張表**——手建的樣板沒有生成鍵，之後重跑不會原地更新，而且版面會跟外掛的不一致。

各表長什麼樣、哪些列欄是條件顯示、哪些格會留佔位符，見 `references/generated-tables.md`（說明用，以外掛實際輸出為準）。外掛裡的「容積檢討工具」與「表格工具快捷面板」也有同一顆「一鍵容積檢討表」按鈕，使用者自己按與請 Claude 呼叫工具，結果相同。

> 需求前提：需連上使用者本機的 Archicad + BIMTeki Studio，**外掛 ≥ v1.1.0**（需求版本見 `references/mcp-compat.md`）。

## 流程

1. **前置檢查**：`bimteki:check_connection`（多開時先 `list_archicad_instances` 選定對象）。看回傳最後一行「版本：」——外掛早於 v1.1.0 或工具清單裡沒有 `generate_area_review_tables`，代表外掛／連接器太舊：請使用者重跑安裝檔並完全重開 Claude；沒有手建退路，不要改用 `create_project_table_template` 自己組這六張表。再 `bimteki:get_project_status`：`project_file.hasFile == false`（專案只在記憶體）要提醒生成後記得另存，否則樣板不會落地；`finalized` 不擋、只提醒。
2. **先看能做哪些**：`bimteki:generate_area_review_tables(dry_run=True)`，回傳 `preflight[]` 每張表 `canBuild` 與 `reason`。帶參數時把關鍵字換成 `tables`（對照表見下）；沒帶參數＝六張全做。
3. **跟使用者確認**：列出可建的表與略過的表（附原因），並說明兩件事——(a) 已生成過的樣板會**整份覆寫**，使用者在編輯器對那些樣板做的修改會消失；(b) 會寫入專案並存檔。不要一次全建而不問。區域缺席（`reason` 是「尚未繪製…區域」）時不代畫、不呼叫任何建立區域的工具，請使用者先畫好匯入再回來。
4. **實跑**：`bimteki:generate_area_review_tables(tables=[...])`（全做就不帶 `tables`）。回 `lockedTables`＝團隊協作有表格被他人保留、**沒有動任何樣板**：把清單轉告使用者請對方釋放（或請使用者在 Archicad 開樣板表格管理器發送釋放要求），不要重試硬闖。
5. **轉述回報**（照回傳欄位，不要自己猜數值）：
   - `created`／`updated`：樣板名與 `templateGuid`；`updated` 附 `placedTableCount`，表示已放置到圖面的表格已同步重繪。
   - `skipped`：略過原因（區域未匯入、沒有地下層、沒有屋突層…）。
   - `stale`：專案裡還掛著生成鍵、但本次沒再產出的舊樣板（例如樓層減少、或舊版生成的屋突樣板），工具**不刪**；要刪需使用者明確同意後用 `manage_project_table_templates` delete。
   - `placeholders`：需人工填寫的格（基地概要的地號／起造人／圖號／法規門檻外情境…），逐項列成待辦。
   - `notes`：版面判斷與提醒（例如一般多棟移除樓高欄、騎樓改綁專案層級、多分區建蔽率請目視確認）。
   - `savedToFile == false`：提醒使用者另存專案。
6. **放置**：樣板都在專案資料夾「容積檢討表」底下。使用者要放到佈圖時用 `bimteki:place_project_table_on_layout`（各層容積與屋突都是每層各一張、各格已綁該層，不必帶 `storyGuid`），或請使用者在表格管理器放置。

## 參數對照（呼叫本 skill 時帶的關鍵字 → `tables`）

| 關鍵字 | 也接受 | `tables` 值 | 產出 |
|---|---|---|---|
| `全部` | `all`、不帶參數 | 省略 | 六張能做的全做 |
| `面積總表` | `area`、面積、樓地板面積 | `summary` | 各層樓地板面積總表（全案一張） |
| `容積` | `volume`、各層容積、地上層容積 | `per_floor_volume` | 各層容積檢討（每地上層一張） |
| `地下` | `basement`、地下層、地下室 | `basement_volume` | 地下層容積檢討（全案一張；明確點名時沒地下層也會建） |
| `屋突` | `rooftop` | `rooftop` | 屋突面積檢討（每屋突層一張，多棟分棟時逐棟） |
| `建蔽` | `coverage`、建蔽率、建築面積檢討 | `coverage` | 建蔽率檢討（表格標題「建築面積檢討」） |
| `基地` | `site`、基地概要、基地資訊 | `site_overview` | 基地概要表 |
| `清單` | `list` | — | 只跑 `dry_run` 列出能做的表，不建 |

「`容積`」是地上層的各層容積檢討，地下層用「`地下`」。比對不到任何一列時列出上表請使用者指定；法規條文類指到 `table-code`，綠化面積檢討指到 `custom-area-review`。

## 例外與退路

- **外掛太舊（< v1.1.0）**：停手，請使用者更新外掛與連接器後再做；不要手建。
- **使用者有自己的範例表（事務所格式）要照抄**：一鍵生成的版面固定；先一鍵生成，再用 `manage_project_table_templates` duplicate 複製一份、用表格編輯器或 `modify_project_table_template` 改成範例的樣子——複本沒有生成鍵，不會被覆寫。
- **使用者想在生成的表上加東西**：提醒重跑會整份覆寫；要保留修改就複製後再改，或改在放置後的表格上（放置表格與樣板同步，也會被覆寫，所以還是建議複製樣板）。
- **基地概要的工程造價三列顯示空白**：綁的是專案造價 token，單價與雜項算式要先在專案資訊面板「工程造價」設定，或由 Claude 問過使用者後 `bimteki:set_project_core_info(cost={...})` 寫入（已定案的案件會被拒絕），再重跑一次即可更新。
- **數值不對**：改專案資料或區域（面積來源、扣除項、停車位數…），不要在表格裡硬改；改完重跑一鍵生成或按「更新自動文字」。

## 注意事項

- 工具只建樣板、不放置到圖面、不刪任何樣板；刪除一律先取得使用者同意。
- `dry_run` 不寫入；實跑會寫入專案並存檔（`hasFile` 為 false 時只在記憶體）。動手前讓使用者知道。
- 同一張表若出現多份生成樣板（`duplicates`），工具只更新第一份；請使用者清掉多餘的那份。
- 不要憑記憶描述表格內容或 token；回答使用者「這張表有哪些列」時以 `references/generated-tables.md` 為準，實際內容以 `get_project_table_templates(template_guid=…)` 讀回為準。
