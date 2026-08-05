# 地下層容積檢討表 — 陣列欄位與 display→token 對照

值一律用 autotext 綁定，由 BIMTeki 即時計算。以下 token 實測在 BIMTeki 專案家族穩定，
`scripts/build_basement_table.py` 已內建同一份預設；**仍建議**用 `get_project_autotext_catalog`
依 display 比對確認，有出入時把該案實際 token 放進 config 的 `tokens` 覆寫，切勿硬編。

## 一、陣列自動文字「地下層停車清單」（分類 arrayField）

- **來源 token（sourceAutoTextToken）**：`ParkingInfoStoryManager.ParkingInfoStories`
- **path**：容積檢討 / 地下層免計容積檢討 / 地下層停車清單
- `isArrayField: true`、`needGUID: false`、`targetType: -858993460`

**可用欄位（fieldName，逐字對）**：
`樓層`、`樓地板面積`、`汽車位數`、`機車位數`、`自行車位數`、`可扣容積計算式`

陣列在儲存格內的編碼（放 col0、`is_array_autotext_root: true`、`originaldata` 為下列字串）：

```
ARRAY_AUTOTEXT_V1:{"sourceAutoTextToken":"ParkingInfoStoryManager.ParkingInfoStories",
"columnSettings":[
  {"fieldName":"樓層","isVisible":true,"displayOrder":0},
  {"fieldName":"汽車位數","isVisible":true,"displayOrder":1},
  {"fieldName":"機車位數","isVisible":true,"displayOrder":2},
  {"fieldName":"樓地板面積","isVisible":true,"displayOrder":3}
],"fieldsOrientation":0,"targetType":-858993460,"needGUID":false,
"propSettingName":"","isTemplateGUID":false,"targetGUID":""}
```

- `columnSettings` 的順序（displayOrder）＝表格欄序，需與欄頭列、小計列一致。
- `isVisible:false` 可保留欄位定義但不顯示；本表一律只放要顯示的欄位。
- `fieldsOrientation:0`＝欄位橫向鋪成欄、陣列各項（樓層）縱向鋪成列。
- 放置到 layout 時才展開；未放置的樣板 `statedata` 顯示原始 JSON 或第一項預覽，屬正常。

## 二、小計列 token（分類 volumeCheck，path 容積檢討/地下層免計容積檢討/總計）

小計列 col0 放文字「小計」；其餘各欄依欄位對應綁下列「總計」token。

| 陣列欄位 | 小計格 display | token |
|----|----|----|
| 汽車位數 | 數量：地下層總計汽車停車位數 | ${TJL$FB92F011BC7FF} |
| 機車位數 | 數量：地下層總計機車停車位數 | ${TJL$F32C0743E2966} |
| 自行車位數 | 數量：地下層總計自行車停車位數 | ${TJL$F1ABD882E5DE2} |
| 樓地板面積 | 面積：地下層總計樓地板面積 | ${TJL$FD90579BEFCB9} |
| 可扣容積計算式 | （無對應總計，該格留空） | — |

## 三、檢討區塊 token

| 表列 | display | token | 分類/path |
|----|----|----|----|
| 防空避難設備面積：（值＋「m² (按建築面積附建)」） | 面積：法定防空避難室面積 | ${TJL$FDB4E6D7607F2} | coverage / 建蔽率相關 |
| 可扣容積總計： | 算式：地下層可扣容積 | ${TJL$F9DDB487BBF2A} | volumeCheck / …/檢討 |
| 檢討：（最終結果） | 算式：地下室容積檢討式 | ${TJL$FF4CBAA811ADC} | volumeCheck / …/檢討 |
| （選用）地下層樓地板面積： | 算式：地下層樓地板面積總計(含車道) | ${TJL$FA76D466BC8B6} | volumeCheck / …/檢討 |

備援/佐證 token（判斷或替代用，通常不直接放表）：
- 面積：地下層可扣容積 ${TJL$F6A7CAF0C3721}
- 面積：地下層回計容積 ${TJL$F70DB6682A741}
- 計算式：法定防空避難室面積計算式 ${TJL$FD872A6CF6EF4}

## 四、常數

- roomGuid（所有容積檢討表共用）：`4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`
- storyGuid：全案總計 story（storyGuidList 中多棟取最後一個「總計：」、單棟取其「總計：」）。
  這些 token 為全案層級、needGUID=false，story 脈絡實務上不影響結果，帶上僅為與內建表一致。

## 五、可扣容積算式的組成（理解用，勿自行改寫）

`算式：地下層可扣容積` 由 BIMTeki 自動組成，形如：
`汽車位數*40 + 機車位數*4 (+ 自行車位數*4) + 防空避難室面積 = 合計m²`
（有自行車才含自行車項；防空避難室面積自動納入）。因此不同專案顯示的項數不同是正常的——
照綁 token 讓 BIMTeki 算，不要把附圖的算式寫死。
最終「檢討：」= `地下層樓地板面積總計 ≤ 可扣容積 → 符合/不符` 也由 `算式：地下室容積檢討式` 自動判斷。
