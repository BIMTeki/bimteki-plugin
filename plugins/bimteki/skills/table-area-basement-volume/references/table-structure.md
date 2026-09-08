# 地下層容積檢討表 — 表格結構規格

全案一張、不分棟。欄數 = 陣列可見欄位數（預設 4）。由上而下逐列如下（以預設 4 欄為例，
欄序：樓層／汽車位數／機車位數／樓地板面積）。規格依內建 sample「地下層容積檢討」與實建驗證而來。

## 一、逐列結構

| row | 內容 | 說明 |
|----|----|----|
| 0 | 標題「地下層容積檢討」 | col0，textsize 1；`merges` colspan=ncols |
| 1 | 欄頭：樓層｜汽車位數｜機車位數｜樓地板面積(m²) | 手打文字，順序＝陣列 columnSettings 順序 |
| 2 | **陣列根**（col0）＋佔位空格 | `is_array_autotext_root:true`＋`ARRAY_AUTOTEXT_V1` originaldata；其餘欄空白 |
| 3 | 小計 | col0 文字「小計」；各欄綁「數量/面積：地下層總計…」token；無對應者留空 |
| 4 | 檢討： | divider，col0 文字；`merges` colspan=ncols；其餘欄空白 |
| 5 | 防空避難設備面積： | col0 標籤；col1 綁「面積：法定防空避難室面積」＋文字「m² (按建築面積附建)」，colspan=ncols-1 |
| 6 | 可扣容積總計： | col0 標籤；col1 綁「算式：地下層可扣容積」，colspan=ncols-1 |
| 7 | 檢討： | col0 標籤；col1 綁「算式：地下室容積檢討式」，colspan=ncols-1 |

**放置時的展開**：陣列根在 row2；放到 layout 後 BIMTeki 依專案停車樓層（例地下二層／地下一層／
地上一層）把 row2 展開成多列，並把 row3 以後往下推。因此「小計」必須緊接陣列根列（row3），
展開後才會正好落在清單下方。merges 定義在**樣板的靜態列索引**上，BIMTeki 放置時會自動平移。

**選用列**：內建 sample 在 divider 後、防空避難前多一列「地下層樓地板面積：」＝
`算式：地下層樓地板面積總計(含車道)`。附圖版本沒有此列（該數值出現在最終檢討式左側），故預設關閉；
需要時設 config `include_floor_area_row: true`。

## 二、儲存格格式

- 全表 `alignment:1`（靠左）、`textbold:false`、`newline:0`、`charwidth:0`。
- textsize：標題列 1、其餘 2。
- 有內容的格帶 `storyGuid`（全案總計）與 `roomGuid`（常數 4f8303bf-…）；純空白佔位格不帶。
- 值格用 `segments`（`{"type":"autotext","token":...}`；需要接文字時再加 `{"type":"text","value":...}`）。
  讀回時 BIMTeki 會把 segments 合成 originaldata 內嵌 `${TJL$...}`，屬正常。
- 陣列根格：不要用 segments，改用 `is_array_autotext_root:true` ＋ `originaldata` = `ARRAY_AUTOTEXT_V1:{...}`。
- 合併只允許單純水平或垂直（本表全是水平 colspan）。
- 框線預設全 1。table_type=normal，不設樣板層級 story_guid/room_guid。

## 三、欄寬與等寬

- 預設 `column_widths`＝樓層欄 150、其餘欄平均分配（腳本自動算）。可用 config 覆寫。
- **關鍵**：`modify_project_table_template` 要帶 `equal_col=[]`。新建表格預設把欄位設成強制等寬
  （讀回 `equalCol` 會變 [0, ncols-1]），會蓋掉 column_widths；清成空陣列才讓欄寬生效。

## 四、build_basement_table.py 的 config

```json
{
  "story_guid": "全案總計 story guid（含大括號）",   // 必填
  "columns": ["樓層","汽車位數","機車位數","樓地板面積"], // 選填；預設此四欄；第一欄須為「樓層」
  "header_labels": {"樓地板面積":"樓地板面積(m²)"},    // 選填；覆寫欄頭顯示名
  "include_floor_area_row": false,                     // 選填；是否加「地下層樓地板面積：」列
  "tokens": {"算式：地下層可扣容積":"${TJL$...}"},       // 選填；覆寫預設 token
  "column_widths": [150,120,120,260],                  // 選填；覆寫欄寬
  "room_guid": "4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3"   // 選填；預設常數
}
```

- `columns` 可加 `自行車位數`（專案有自行車位時）或 `可扣容積計算式`（逐列顯示各層算式）。
- 輸出 `cells` 直接餵 `create_project_table_template`；`merges`/`column_widths` 於 `modify` 帶入
  （modify 另加 `equal_col=[]`）。
