# BIMTeki 建照檢討 Skills

BIMTeki Studio 的 AI 技能包，可在 **Claude**（Claude Code／Cowork）或 **ChatGPT 桌面版／Codex** 使用。安裝後，你可以直接用中文交代工作，AI 助理會操作 Archicad 中開啟的 BIMTeki 專案，自動產生建照圖說所需的各式檢討表格。

> 例如：「幫這案做各層樓地板面積總表」「做地下層容積檢討表」「把這份土管做成檢討表」

---

## 技能清單

| 技能 | 用途 |
|---|---|
| `table` | **檢討表清單**。`/bimteki:table 清單` 列出本案可做的表，並指到下面兩個分類入口 |
| `table-area` | **面積與容積檢討表入口**。`/bimteki:table-area <關鍵字>` 直接做指定的表（area 面積總表／volume 各層容積／basement 地下層／rooftop 屋突／coverage 建蔽率／site 基地概要／green 綠化） |
| `table-code` | **法規條文檢討表入口**。`/bimteki:table-code <關鍵字>` 直接做指定的表（permit 建照審查／landuse 土管／a11y 無障礙） |
| `table-area-summary` | 各層樓地板面積總表 |
| `table-area-per-floor-volume` | 各層容積檢討表（每個地上層一張） |
| `table-area-basement-volume` | 地下層容積檢討表 |
| `table-area-rooftop` | 屋突面積檢討表 |
| `table-area-site-overview` | 基地概要表 |
| `table-area-coverage` | 建蔽率檢討表（建築面積檢討） |
| `custom-area-review` | 自訂面積項目檢討（依你提供的檢討方式做面積比例檢討，例：宜居建築垂直綠化；需「自訂面積項目檢討」模組授權）。直接跟 Claude 說「做自訂面積項目檢討」即可，不經 `table` 入口 |
| `table-code-permit` | 建造執照規定項目審查表（第 18~27 項） |
| `table-code-landuse` | 依土管文件生成土管檢討表 |
| `table-code-accessibility` | 無障礙建築檢討表 |
| `project-info-fill` | 把專案資料夾裡的建築／土地資料回填到 BIMTeki 專案資訊 |
| `lawname-index` | 容積區域請照空間名稱 GDL 參數索引 |

---

## 安裝前請先確認

1. **Claude 付費方案**（Pro、Max、Team 或 Enterprise；免費方案無法安裝外掛），**或 ChatGPT 任一方案**（Codex 含在所有方案，需安裝 ChatGPT 桌面版）。
2. **已執行 BIMTeki Studio 安裝檔**（見下方步驟一），且授權正常。
3. 使用時 **Archicad 要開著、且已開啟要檢討的專案**。
4. 目前僅支援 **Windows**。

---

## 步驟一：執行 BIMTeki Studio 安裝檔

技能本身只是「作業指示」，實際去讀寫 Archicad 的是 BIMTeki Studio 外掛與它的 MCP 連接器（Claude、ChatGPT 桌面版／Codex 共用同一個）。

安裝時請確認 **「AI 助理連接器 (BIMTeki MCP)」**（舊版安裝檔叫「Claude AI 連接器」）這個項目是勾選的（預設就會勾）。它會把
連接器裝到 `C:\Program Files\BIMTeki Studio\mcp\`，**連 Python 都自帶**，你不需要另外安裝任何東西。

> 已經裝過舊版 BIMTeki Studio 的人，請重新執行一次最新版安裝檔，才會有這個連接器。

---

## 步驟二：安裝技能包

### Claude Code CLI

在任一專案下啟動 `claude`，然後依序執行：

```
/plugin marketplace add BIMTeki/bimteki-plugin
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
https://github.com/BIMTeki/bimteki-plugin
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

### ChatGPT 桌面版／Codex

ChatGPT 桌面版（Windows 版由 Microsoft Store 安裝）左上角可以切換 **ChatGPT** 與 **Codex** 兩種模式，
**BIMTeki 要切到 Codex 模式使用**；Codex 含在所有 ChatGPT 方案內，桌面版與 Codex CLI 共用同一套設定，裝一次兩邊都能用。
ChatGPT 模式與網頁版只接受遠端 MCP，連不到本機的連接器（和 Claude 的 Cowork／Chat 分工是同一回事）。

**方式一（建議）：從 marketplace 安裝**

在終端機執行：

```
codex plugin marketplace add BIMTeki/bimteki-plugin
```

然後在桌面版切到 **Codex** 模式 → 左側 **外掛程式** → **個人** 分頁，會看到「BIMTeki 建照檢討」，按 **＋** 安裝
（Codex CLI 則是輸入 `/plugins`）。技能包會自動帶上連接器設定（外掛會標示「Desktop only」，因為連接器只能在本機執行）。
裝完請**完全關閉並重新開啟 ChatGPT 桌面版**。

**方式二：下載安裝包**

到 [Releases](https://github.com/BIMTeki/bimteki-plugin/releases) 下載 `bimteki-skills-portable-v○.○.○.zip`，解壓縮後在 PowerShell 執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install-for-codex.ps1
```

它會把連接器設定寫進 `%USERPROFILE%\.codex\config.toml`（其他設定不動、先備份）、把技能複製到
`%USERPROFILE%\.codex\skills\`（Codex 專用，不會跟 Claude 的技能包重複），最後真的啟動連接器驗證一次。這個方式裝的技能名稱前面會多 `bimteki-`。
移除用 `.\install-for-codex.ps1 -Uninstall`。

**驗證**：在 Codex 輸入 `/mcp` 應看到 `bimteki`；`/skills` 應看到 BIMTeki 的技能。之後直接用中文交代即可；
要指定技能可打 `$table-area-summary`（方式一）或 `$bimteki-table-area-summary`（方式二），ChatGPT 對話框則用 `@` 選技能。

### Google Antigravity（實驗性）

用方式二的安裝包，改跑 `install-for-antigravity.ps1`，細節見安裝包內的 README。
Gemini 網頁版／手機 app 目前無法連接本機連接器。

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

如果想直接指定某個技能，也可以打斜線：

```
/bimteki:table-area-summary
```

（ChatGPT 桌面版／Codex 則輸入 `$table-area-summary`，或在 ChatGPT 對話框用 `@` 選技能。）

---

## 疑難排解

### 第一步：跑檢查腳本

只要是「Claude／ChatGPT 看不到 BIMTeki 工具」這一類的問題，**先跑這一支**，不用自己猜是哪裡壞掉。
它隨 BIMTeki Studio 一起安裝，只讀不寫，不會改動任何東西。

在 PowerShell 貼上執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:ProgramW6432\BIMTeki Studio\verify-mcp-install.ps1"
```

它會依序檢查登錄檔、檔案是否齊全，然後真的啟動連接器跑一次連線握手，最後告訴你卡在哪一關。

看到 **「全部通過」** ＝ 這台機器的連接器沒問題，問題在 AI 助理端（往下看下面兩節）。

最後一行會印出 **MCP 版本**，回報問題時請一併附上。技能包（`/plugin` 一鍵更新）和連接器
（要重跑安裝檔）是**分開更新**的，所以兩邊版本不一樣是常態；有疑問時把這個版本號告訴我們最快。

看到紅色 **[失敗]**，對照處理：

| 失敗的項目 | 意思與處理方式 |
|---|---|
| 登錄檔：找不到 | 安裝時沒勾「AI 助理連接器 (BIMTeki MCP)」（舊版叫「Claude AI 連接器」），或安裝檔是加入連接器之前的舊版。重跑最新版安裝檔 |
| 內嵌 Python / MCP 進入點 不存在 | 檔案不齊，重跑安裝檔 |
| 預編譯 .pyc 太少 | 不影響功能，但連接器啟動會變慢。重跑安裝檔可修正 |
| initialize 沒有回應 | 多半是防毒或公司資安軟體擋掉了連接器。請 IT 把 `BIMTeki Studio\mcp\python\python.exe` 加入白名單 |
| stdout 被汙染 | 請把完整輸出寄給我們 |

安裝時若看到「安裝位置不是預設」的提示，代表安裝到了非標準位置，marketplace 技能包（用固定路徑）將無法自動連上；請用預設位置重裝，或改用安裝包的 `install-for-codex.ps1`（它會讀登錄檔找到實際位置）。

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
| Claude 說「你的 MCP 版本太舊」，或表格少了合併儲存格／框線 | 技能包更新了、連接器沒有。**重跑最新版 BIMTeki Studio 安裝檔**，裝完完全關掉再重開 Claude |
| 授權相關錯誤 | 請聯繫 BIMTeki |

### ChatGPT 桌面版／Codex 端

| 症狀 | 處理方式 |
|---|---|
| `/mcp` 沒有 bimteki | 重跑一次 `install-for-codex.ps1`，或確認 `%USERPROFILE%\.codex\config.toml` 內有 `[mcp_servers.bimteki]`；改完要完全重開 ChatGPT 桌面版 |
| bimteki 顯示啟動失敗／逾時 | Windows Defender 第一次掃描內嵌 Python 會超過 Codex 預設的 10 秒。安裝腳本已設 30 秒；用 marketplace 裝的請在 `config.toml` 的 `[mcp_servers.bimteki]` 下加一行 `startup_timeout_sec = 30` |
| 技能沒出現 | 方式一：確認 Plugins 內 BIMTeki 為啟用；方式二：確認 `%USERPROFILE%\.codex\skills\` 底下有 `bimteki-*` 資料夾；ChatGPT 桌面版仍沒顯示時改跑 `.\install-for-codex.ps1 -SkillsDir "$HOME\.agents\skills"` |
| ChatGPT 模式或網頁版看不到工具 | 正常。本機連接器只有 Codex 模式（桌面版左上角切換）與 Codex CLI 連得到 |

若上述都無法解決，請聯繫 office@arkiteki.com，並附上**檢查腳本的完整輸出**、AI 助理的錯誤訊息與 Archicad 版本。

---

## 授權與支援

本技能包供 BIMTeki Studio 授權使用者使用。技能本身需搭配 BIMTeki Studio 外掛與有效授權才能運作。

聯絡：office@arkiteki.com

---

<sub>此 repo 為發佈用產物，由 BIMTeki 內部開發 repo 自動生成，請勿直接在此修改。</sub>
