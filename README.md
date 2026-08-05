# BIMTeki 建照檢討 Skills

BIMTeki Studio 的 Claude 技能包。安裝後，你可以直接用中文交代工作，Claude 會操作 Archicad 中開啟的 BIMTeki 專案，自動產生建照圖說所需的各式檢討表格。

> 例如：「幫這案做各層樓地板面積總表」「做地下層容積檢討表」「把這份土管做成檢討表」「畫容積區域」

---

## 技能清單

| 技能 | 用途 |
|---|---|
| `bimteki-review-tables` | **檢討表總調度**。不確定要做哪張表時，先叫這個 |
| `bimteki-area-summary-table` | 各層樓地板面積總表 |
| `bimteki-per-floor-volume-review-table` | 各層容積檢討表（每個地上層一張） |
| `bimteki-basement-volume-review-table` | 地下層容積檢討表 |
| `bimteki-rooftop-area-review-table` | 屋突面積檢討表 |
| `bimteki-site-overview-table` | 基地概要表 |
| `bimteki-coverage-review-table` | 建蔽率檢討表（建築面積檢討） |
| `bimteki-green-area-review-table` | 綠化面積檢討表 |
| `bimteki-permit-review-table` | 建造執照規定項目審查表（第 18~27 項） |
| `bimteki-landuse-review-table` | 依土管文件生成土管檢討表 |
| `bimteki-accessibility-review-table` | 無障礙建築檢討表 |
| `bimteki-project-info-fill` | 把專案資料夾裡的建築／土地資料回填到 BIMTeki 專案資訊 |
| `bimteki-volume-zones-v2` | 在 Archicad 中繪製容積區域 |
| `bimteki-lawname-index` | 容積區域請照空間名稱 GDL 參數索引 |
| `bimteki-wall-display-doctor` | 診斷牆體顯示異常（唯讀，不會改你的模型） |

---

## 安裝前請先確認

1. **Claude 付費方案**（Pro、Max、Team 或 Enterprise）。免費方案無法安裝外掛。
2. **Archicad 已安裝 BIMTeki Studio 外掛**，且授權正常。
3. **BIMTeki MCP 已安裝**（見下方步驟一）。
4. 使用時 **Archicad 要開著、且已開啟要檢討的專案**。

---

## 步驟一：安裝 BIMTeki MCP

技能本身只是「作業指示」，實際去讀寫 Archicad 的是 BIMTeki MCP。沒有它，所有技能都無法運作。

### Claude 桌機版 / Cowork

1. 向 BIMTeki 索取 `bimteki-mcp.mcpb`
2. 打開 Claude Desktop → **設定 (Settings)** → **擴充功能 (Extensions)**
3. 把 `bimteki-mcp.mcpb` 拖進去，或選「從檔案安裝」
4. 安裝完成後，確認該擴充功能為「已啟用」

### Claude Code CLI

1. 向 BIMTeki 索取 `bimteki-mcp.mcpb`（它其實是一個 zip）
2. 解壓縮到一個固定位置，建議 `C:\BIMTeki\mcp`
3. 在終端機執行（路徑請改成你實際解壓的位置）：

```powershell
claude mcp add bimteki --scope user -e PYTHONUTF8=1 -e "PYTHONPATH=C:\BIMTeki\mcp;C:\BIMTeki\mcp\lib" -- python "C:\BIMTeki\mcp\server\main.py"
```

4. 用 `claude mcp list` 確認 `bimteki` 出現且狀態正常

---

## 步驟二：安裝技能包

### Claude Code CLI

在任一專案下啟動 `claude`，然後依序執行：

```
/plugin marketplace add GOLLd765/bimteki-plugin
/plugin install bimteki@bimteki
```

安裝時會問你安裝範圍，選 **User scope**（所有專案都能用）。

若安裝摘要顯示 `Run /reload-plugins to activate.`，就再執行一次：

```
/reload-plugins
```

### Claude Cowork（桌機版）

1. 打開 Claude 桌機版 → 切到 **Cowork** 分頁
2. 左側選單點 **Customize（自訂）** → **Plugins（外掛）**
3. 在 **Personal plugins** 區塊按 **+** → **Add marketplace**
4. 選 **Add from a repository**，貼上：

```
https://github.com/GOLLd765/bimteki-plugin
```

5. 在出現的清單中找到 **BIMTeki 建照檢討**，按 **Install**

安裝完成後，在對話框輸入 `/` 或按 `+`，就會看到所有 BIMTeki 技能。

---

## 步驟三：開啟自動更新（建議）

第三方技能包預設**不會**自動更新。建議手動打開：

**Claude Code CLI**

1. 執行 `/plugin`
2. 切到 **Marketplaces** 分頁
3. 選 **bimteki**
4. 選 **Enable auto-update**

也可以隨時手動更新：

```
/plugin marketplace update bimteki
```

**Cowork**：在 Customize → Plugins 中對 BIMTeki 技能包按更新即可。

---

## 怎麼使用

安裝完就可以直接用中文交代，不需要記指令名稱：

> 「幫我做這案的面積總表」
> 「做地下層容積檢討表」
> 「這個建照有哪些檢討表可以做？」
> 「把這份土管做成檢討表」（並把土管 PDF 拖進對話）
> 「幫我畫容積區域」

如果想直接指定某個技能，也可以打斜線：

```
/bimteki:bimteki-area-summary-table
```

---

## 疑難排解

| 症狀 | 處理方式 |
|---|---|
| 技能沒出現在清單裡 | 執行 `/reload-plugins`；仍無效就重開 Claude |
| `/plugin` 指令不存在 | Claude Code 版本太舊，請更新到最新版 |
| Claude 說「找不到 BIMTeki 工具」 | MCP 沒裝或沒啟用，回到步驟一 |
| Claude 說「無法連線到 Archicad」 | 確認 Archicad 開著、專案已開啟、BIMTeki 外掛已載入 |
| 表格產生了但數值是空白 | 自動文字要放置到圖紙（Layout）上才會計算出實際值 |
| 授權相關錯誤 | 請聯繫 BIMTeki |

若上述都無法解決，請聯繫 office@arkiteki.com，並附上 Claude 的錯誤訊息與 Archicad 版本。

---

## 授權與支援

本技能包供 BIMTeki Studio 授權使用者使用。技能本身需搭配 BIMTeki Studio 外掛與有效授權才能運作。

聯絡：office@arkiteki.com

---

<sub>此 repo 為發佈用產物，由 BIMTeki 內部開發 repo 自動生成，請勿直接在此修改。</sub>
