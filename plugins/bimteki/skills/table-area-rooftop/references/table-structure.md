# 屋突面積檢討表 — 結構規格

2 欄、固定 4 列。標題跨兩欄；每列左欄固定標籤、右欄值。三個值都是**樓層屬性（story 相依）**自動文字。

## 列

| 列 | col0（標籤） | col1（值，story 相依） |
|----|----|----|
| 0 標題 | segments：[（多棟分棟才有）棟別 autotext]＋樓層名稱 autotext＋text「面積檢討」；colspan 2、textsize 1 | （空，被合併蓋住） |
| 1 屋突面積 | text「屋突面積：」 | storyArea「算式：室內樓地板面積」（或「算式：屋突」），newline 3 |
| 2 允建屋突面積 | text「允建屋突面積：」 | roofArea「算式：屋突允建面積」 |
| 3 檢討 | text「檢討：」 | roofArea「算式：屋突檢討式」 |

## 樓層屬性綁定（兩種）

- **story-open（單一樣板，建議）**：儲存格不帶 storyGuid。建表後用 `modify_project_table_template`
  設 `table_type="story"`、`story_guid=""`（清空＝樓層打開）。放置時使用者自選樓層，
  三個 story 相依自動文字（屋突面積／允建屋突面積／檢討）＋標題（樓層名稱／棟別）皆依放置樓層與其棟別解析。
  單棟／多棟分棟／各棟總計共用同一樣板。
- **per-story（逐棟逐屋突層各一張）**：每格帶該屋突層 storyGuid；同一組 token 換 storyGuid 即得該層值，
  各棟各屋突層各建一張。

## 格式

全表 alignment 1、textbold false、charwidth 0。textsize：標題 1、其餘 2。newline：值格 3、其餘 0。
roomGuid 一律常數 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`。merges：標題 {row0,col0,colspan2,rowspan1}。
欄寬預設 [220, 616]（可用 config column_widths / value_col_width 覆寫）。

## config（build_rooftop_table.py）

```json
{
  "story_open": true,
  "story_guid": "per-story 模式各格綁的屋突層 story guid",
  "block_prefix": true,
  "area_token_display": "算式：室內樓地板面積",
  "allow_token": "${TJL$...}",
  "review_token": "${TJL$...}",
  "tokens": { "算式：屋突": "${TJL$...}" },
  "column_widths": [220, 616]
}
```
- story_open=true：樣板層級樓層打開（建表後 MCP 設 table_type="story"、story_guid=""），值格不帶 story；三個值預設綁好。
- story_open=false：給 story_guid（該屋突層），值格綁該層。
- block_prefix=true：標題加棟別 autotext（多棟分棟檢討）。
- allow_token/review_token：預設綁「算式：屋突允建面積」「算式：屋突檢討式」；給空字串則該格留空。
