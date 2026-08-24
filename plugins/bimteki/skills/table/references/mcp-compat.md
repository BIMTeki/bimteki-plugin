# 版本相容對照（skills ↔ MCP ↔ 外掛 ↔ 圖庫）

**這份是需求版本的單一事實來源。** 各表 spoke skill 不要各自宣告需求版本，一律回到這裡。

## 為什麼需要這份文件

BIMTeki 有四條**各自進版**的版本線，使用者手上的組合不保證跟你手上的 skill 同期：

| 版本線 | 使用者怎麼更新 |
|---|---|
| skills（本技能包） | `/plugin marketplace update bimteki`，一鍵 |
| MCP server（Claude 連接器） | 重跑 BIMTeki Studio 安裝檔 |
| 外掛（Archicad Add-On） | 重跑 BIMTeki Studio 安裝檔 |
| GDL 圖庫 | 重跑 BIMTeki Studio 安裝檔 |

skills 更新是**一鍵**、其他三條要**重跑安裝檔**，所以「skill 很新、MCP 很舊」是常態，不是異常。
四條線不需要、也不應該對齊成同一個數字——要的是「用之前先問清楚對方是幾版」。

## 怎麼問到版本

`bimteki:check_connection` 的回傳最後一行就是：

```
版本：MCP v0.8.0+ccbf989／外掛 v0.0.11／圖庫 v1.0.9
```

- **MCP 版本**：MCP 自己讀安裝目錄的 `mcp-version.txt`。`+` 後面是打包當下的 git sha，
  `.dirty` 代表打包時工作目錄有未提交改動（不該出現在正式版）。
- **外掛／圖庫版本**：由外掛的 `Get_License_Status` 回報，**外掛 v0.0.11 起才有**；
  更舊的版本會顯示「未回報（外掛早於 v0.0.11）」——那本身就代表使用者的外掛很舊。
- 連不上 Archicad 時仍會回報 MCP 版本（那是讀本機檔案），對診斷「裝錯版本」有用。

### ⚠️ 完全沒有「版本：」這一行時

代表使用者的 **MCP 早於 v0.8.0**（版本回報是 0.8.0 才加的）。

**這種情況不要停手、不要當成版本不足**——0.7.x 一樣做得了所有檢討表。照常往下走，
真正該看的是「工具有沒有你要用的參數」（見下一節）。可以順口提一句建議更新，但不要擋。

判斷順序是這樣：

| 觀察到的 | 代表 | 該做什麼 |
|---|---|---|
| 有「版本：」行 | MCP ≥ 0.8.0 | 照版本號判斷 |
| 沒有「版本：」行，但 `create_project_table_template` 有 `merges` 參數 | MCP 介於 0.7.1～0.7.x | 照常建表，可建議更新 |
| 沒有「版本：」行，且 `create` 沒有 `merges` 參數 | MCP < 0.7.1 | 停手，請使用者重跑安裝檔 |

## 目前的需求版本

| 功能 | 需求 | 沒有的話會怎樣 |
|---|---|---|
| 所有檢討表 spoke skill 的建表流程 | **MCP ≥ 0.7.1** | `create_project_table_template` 不接受 `merges` / `equal_col` / 框線參數，必須退回「先 create 再 modify 補」的舊兩步流程 |
| 版本回報本身 | MCP ≥ 0.8.0、外掛 ≥ 0.0.11 | 問不到版本，只能靠使用者跑 `verify-mcp-install.ps1` 回報 |
| 自訂面積項目檢討表（`table-custom-area`）的基本流程 | **MCP ≥ 0.11.0**（另需訂閱含「自訂面積項目檢討」模組授權；試用方案不含） | 工具清單裡沒有 `get_project_custom_area_review`／`set_project_custom_area_review`，無法建檢討項目與匯入區域——停手請使用者重跑安裝檔；授權不足時工具回 `error_code="feature_not_licensed"`，請使用者聯絡 BIMTeki 客服 |
| ↳ 其中的**區域組合**（`create_group`／`rename_group`／`delete_group`／`add_zones_to_group`／`remove_zones_from_group`） | **MCP ≥ 0.12.0** | `set_project_custom_area_review` 的說明裡沒有 `create_group`——多顆填充構成同一個量時只能退回表格內 `{=a+b+c}` 湊合計，要跟使用者說明這是版本限制而非設計 |

> 注意 MCP 工具的**參數本來就是自我描述的**：舊版 MCP 不會把 `merges` 放進 schema，
> 所以你不會「送了一個不存在的參數」。真正的風險是——skill 叫你帶 `merges`、
> 工具卻沒有這個參數，此時**不要硬湊、不要以為是自己記錯**，那就是版本太舊。
> 照下面的處理方式回報使用者。

## 版本不足時怎麼處理

只有上面那張表判定為 **MCP < 0.7.1** 時才算版本不足。此時**停手，講清楚，不要自己想辦法繞過**：

```
你的 BIMTeki MCP 是 v0.6.2，這張表需要 v0.7.1 以上。
請重新執行最新版的 BIMTeki Studio 安裝檔（安裝時確認勾選「Claude AI 連接器 (BIMTeki MCP)」），
裝完後完全關掉再重開 Claude Code。
```

不要因為版本舊就改用舊流程默默把表建出來——使用者會拿到一張跟預期不同的表卻不知道為什麼。

## 維護規則

1. MCP 的工具或參數有增減時，**先進版再打包**（加工具＝minor，破壞相容＝major），
   不要讓兩套不同的工具集共用同一個版本號。
2. 加了新工具或新參數，**同時在上面「目前的需求版本」補一列**，否則 skill 端無從判斷。
3. 需求版本只寫在這份文件；spoke skill 內文一律指回這裡，不要各自寫死版本號（會漏改）。
