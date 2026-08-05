# BIMTeki 建照檢討 Skills

BIMTeki Studio 的 Claude 技能包。安裝後，你可以直接用中文交代工作，Claude 會操作 Archicad 中開啟的 BIMTeki 專案，自動產生建照圖說所需的各式檢討表格。

> 例如：「幫這案做各層樓地板面積總表」「做地下層容積檢討表」「把這份土管做成檢討表」「畫容積區域」

---

## 技能清單

| 技能 | 用途 |
|---|---|
| `table` | **檢討表單一入口**。`/bimteki:table <關鍵字>` 直接做指定的表（permit 建照審查／coverage 建蔽率／area 面積總表／volume 各層容積／basement 地下層／rooftop 屋突／landuse 土管／a11y 無障礙／site 基地概要／green 綠化）；不帶參數則列出本案可做的表讓你挑 |
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
2. **已執行 BIMTeki Studio 安裝檔**（見下方步驟一），且授權正常。
3. 使用時 **Archicad 要開著、且已開啟要檢討的專案**。
4. 目前僅支援 **Windows**。

---

## 步驟一：執行 BIMTeki Studio 安裝檔

技能本身只是「作業指示」，實際去讀寫 Archicad 的是 BIMTeki Studio 外掛與它的 Claude 連接器。

安裝時請確認 **「Claude AI 連接器 (BIMTeki MCP)」** 這個項目是勾選的（預設就會勾）。它會把
連接器裝到 `C:\Program Files\BIMTeki Studio\mcp\`，**連 Python 都自帶**，你不需要另外安裝任何東西。

> 已經裝過舊版 BIMTeki Studio 的人，請重新執行一次最新版安裝檔，才會有這個連接器。

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

> **不需要設定 MCP。** 技能包裡已經帶了連接器設定，會自動找到步驟一裝好的 BIMTeki MCP，
> 你不必執行 `claude mcp add`，也不必安裝任何擴充功能。

### ⚠️ 桌機版請務必在 Cowork 分頁使用，不是 Chat 分頁

Claude 桌機版有兩個分頁，**BIMTeki 只在 Cowork 分頁能實際操作 Archicad**：

| 分頁 | 技能看得到 | 能操作 Archicad |
|---|---|---|
| **Cowork** | ✅ | ✅ |
| Chat | ✅ | ❌ |

在 Chat 分頁一樣叫得出技能、Claude 也會讀取技能內容，但**連不上 Archicad**，最後會回你「找不到 BIMTeki 工具」。這不是安裝失敗，只是分頁用錯了。

（Claude Code CLI 沒有這個區分，直接就能用。）

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

### 第一步：跑檢查腳本

只要是「Claude 看不到 BIMTeki 工具」這一類的問題，**先跑這一支**，不用自己猜是哪裡壞掉。
它隨 BIMTeki Studio 一起安裝，只讀不寫，不會改動任何東西。

在 PowerShell 貼上執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:ProgramW6432\BIMTeki Studio\verify-mcp-install.ps1"
```

它會依序檢查登錄檔、檔案是否齊全，然後真的啟動連接器跑一次連線握手，最後告訴你卡在哪一關。

看到 **「全部通過」** ＝ 這台機器的連接器沒問題，問題在 Claude 端（往下看下一節）。

看到紅色 **[失敗]**，對照處理：

| 失敗的項目 | 意思與處理方式 |
|---|---|
| 登錄檔：找不到 | 安裝時沒勾「Claude AI 連接器 (BIMTeki MCP)」，或安裝檔是加入連接器之前的舊版。重跑最新版安裝檔 |
| 內嵌 Python / MCP 進入點 不存在 | 檔案不齊，重跑安裝檔 |
| 預編譯 .pyc 太少 | 不影響功能，但連接器啟動會變慢。重跑安裝檔可修正 |
| initialize 沒有回應 | 多半是防毒或公司資安軟體擋掉了連接器。請 IT 把 `BIMTeki Studio\mcp\python\python.exe` 加入白名單 |
| stdout 被汙染 | 請把完整輸出寄給我們 |

安裝時若看到「安裝位置不是預設」的提示，代表安裝到了非標準位置，Claude 將無法自動連上；請用預設位置重裝。

### Claude 端

| 症狀 | 處理方式 |
|---|---|
| **桌機版：Claude 說「找不到 BIMTeki 工具」** | **十之八九是用到 Chat 分頁了。切到 Cowork 分頁再試一次** |
| 桌機版：技能包裝了卻不是最新版、Update 按鈕是灰的 | Claude 手上的目錄是快取的。重開 Claude Desktop，或把 marketplace 移除後重新加入 |
| 技能沒出現在清單裡 | 執行 `/reload-plugins`；仍無效就重開 Claude |
| `/plugin` 指令不存在 | Claude Code 版本太舊，請更新到最新版 |
| 檢查腳本全過，但 Claude 仍看不到工具 | 先確認是 Cowork 分頁；再確認技能包為啟用狀態（`/plugin` → Installed），必要時 `/reload-plugins` |
| `/plugin` 的 Errors 分頁顯示連接器啟動失敗 | 跑上面的檢查腳本，依結果處理 |
| Claude 說「無法連線到 Archicad」 | 連接器正常但 Archicad 沒開。確認 Archicad 開著、專案已開啟、BIMTeki 外掛已載入 |
| 表格產生了但數值是空白 | 自動文字要放置到圖紙（Layout）上才會計算出實際值 |
| 授權相關錯誤 | 請聯繫 BIMTeki |

若上述都無法解決，請聯繫 office@arkiteki.com，並附上**檢查腳本的完整輸出**、Claude 的錯誤訊息與 Archicad 版本。

---

## 授權與支援

本技能包供 BIMTeki Studio 授權使用者使用。技能本身需搭配 BIMTeki Studio 外掛與有效授權才能運作。

聯絡：office@arkiteki.com

---

<sub>此 repo 為發佈用產物，由 BIMTeki 內部開發 repo 自動生成，請勿直接在此修改。</sub>
