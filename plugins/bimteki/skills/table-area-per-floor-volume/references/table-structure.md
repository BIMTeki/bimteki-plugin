# 各層容積檢討表 — 表格結構規格

每一地上「樓層群」一張表——一般地上層是「一個 story」，但有夾層的地上層是「當層＋夾層＋小計」
三個 story 合併成一張表，不是三張。版面由「案型」與「該層有沒有夾層」兩條獨立軸決定：
- **single**（單棟、無夾層）：3 欄＝段標籤／項目／值。
- **columns**（連棟透天、無夾層）：3＋棟數 欄＝段標籤／項目／各棟值；標題後有棟別列。
- **blockrows**（一般多棟、無夾層）：4 欄＝段標籤／項目／棟別／值。
- **mezz_single**（單棟＋夾層）：4 欄＝項目／當層／夾層／小計。
- **mezz**（一般多棟＋夾層）：5 欄＝項目／當層/夾層/小計／各棟…／各棟總計小計。

四段由上而下：**當層樓地板面積(A)、免計容積(B)、回計容積(C)、(A)-(B)+(C)**。
值欄全部用 storyArea 的「算式：」autotext。規格由兩案（共用/多棟、連棟透天）實表逐格實測而來。

## 一、案型 → 版面

| 案型 | 判斷 | 版面 | 欄數 | 值格 story |
|----|----|----|----|----|
| 單棟 | block_mode=false | single | 3 | 該地上層 story |
| 單棟＋夾層 | block_mode=false 且該層有配對「…夾層」樓層 | mezz_single | 4 | 見「夾層版面（單棟）」 |
| 一般多棟 | block_mode=true 且 storyGuidList 有「各棟總計地上X層」 | blockrows | 4 | 見下 |
| 一般多棟＋夾層 | 同上，且該層有配對的「…夾層」樓層 | mezz | 5 | 見「夾層版面（多棟）」 |
| 連棟透天 | block_mode=true 且**無**「各棟總計地上X層」（或使用者告知） | columns | 3＋棟數 | 各棟該層 |

**判斷優先序（務必按此順序，不要顛倒）**：先判是否為連棟透天／一般多棟／單棟（決定「案型」這條軸），
**再獨立判該層有沒有配對的「…夾層」樓層**（決定「要不要用 mezz」這條軸）——這兩條軸互相獨立，
案型軸只負責挑出 mezz_single 還是 mezz 兩個變體之一，不能拿「這是單棟案」當理由跳過夾層判斷、
退回把該層／其夾層／其小計當三個獨立樓層各建一張 single 版面表（此為本 skill 已知踩過的錯誤，
起因是誤把「案型→版面」對照表當成唯一判斷依據，沒有另外檢查該層是否存在配對夾層）。

共用/非共用（shared_hall）與案型獨立，只影響 B、C 段哪些列出現（見第三節）。

**一般多棟（blockrows）的展開**：當層樓地板面積(A) 段的**室內面積、陽台面積、陽台>2m** 這三項，
把「項目名」獨立成一欄（col1）並**垂直合併**跨該項的 各棟＋小計 列；旁邊「棟別欄」（col2）逐列放
A棟／B棟／…／小計；值欄（col3）同一「算式：」autotext，各列 storyGuid 指到**該棟該層**、
小計列指到**各棟總計該層**（實測 A棟室內 46.43／B棟 46.36，同 token 換 storyGuid 即得各棟值）。
其餘 A 段項目、以及 B、C、(A)-(B)+(C) 各列不分棟，項目名（col1）以 **colspan 2** 橫跨 項目＋棟別 兩欄、
值放 col3、綁「各棟總計」story。（storyArea 沒有分棟面積 token，分棟明細亦內含在各棟 story 的算式字串中。）

## 二、列與段（骨架）

- **標題列**（1 列）：col0 放標題，`merges` colspan＝總欄數，`textsize:1`。
  segments = [autotext 樓層名稱, text「容積檢討」]（樓層名 token 回傳「地上二層」不含棟別，標題乾淨）。
- **棟別列**（僅 columns/連棟透天，1 列）：col0 text「棟別」（charwidth1）、col1 空、各棟欄放 autotext「棟別」
  綁該棟 story（自動顯示 A棟／B棟…）。
- **當層樓地板面積(A)**：single/columns 為 7 列；blockrows 為 7+棟數×2 列（前三項各展 棟數+1 列）。
  col0 段標籤 rowspan＝該段實際列數。項目依序：室內面積、陽台面積、陽台>2M、室內1/8或8m²、
  陽台1/8檢討、陽台最終面積、當層樓地板面積。
  **陽台面積為 0 的樓層**（判斷見第三節，config 帶 `omit_balcony:true`）移除陽台相關五列
  （陽台面積、陽台>2M、室內1/8或8m²、陽台1/8檢討、陽台最終面積），只剩 室內面積、當層樓地板面積：
  single/columns 為 2 列；blockrows 為 2+棟數 列（僅室內面積展開）。
  **工廠類建築**（判斷見第三節，config 帶 `factory_mode:true`）A 段只放 室內面積、陽台面積、
  當層樓地板面積 三列（移除 陽台>2M、室內1/8或8m²、陽台1/8檢討、陽台最終面積）：
  single/columns 為 3 列；blockrows 為 3+棟數×2 列（室內面積、陽台面積展開）。
  兩者可疊加（工廠類且陽台為 0 → 只剩 室內面積、當層樓地板面積）。
- **免計容積(B)**（動態，n 列）／**回計容積(C)**（動態，m 列）：col0 段標籤 rowspan。項目候選見第三節。
  若 n 或 m 為 0，該段整段不出現。
- **(A)-(B)+(C)**（1 列，段標籤不合併）：項目「容積樓地板面積：」、值「算式：容積樓地板面積」。
  col0 段標籤**依是否有 B/C 段動態顯示**：起於「(A)」，有 B 段才接「-(B)」、有 C 段才接「+(C)」。
  故：有B有C→(A)-(B)+(C)；只有B→(A)-(B)；只有C→(A)+(C)；皆無→(A)。

各段 col0 段標籤只放段第一列，其餘列 col0 為空格（被 rowspan 蓋住）。

## 三、A 段工廠類/陽台過濾、免計(B)、回計(C) 段的項目與出現條件

**A 段工廠類建築過濾**：`get_project_core_snapshot` 的 `review_settings.balcony_in_floor_area.value`
為 true（面板標籤「工廠類建築（陽台全額計入容積樓地板面積計算）」）→ 陽台全額計入、不做 1/8
免計檢討，A 段只放 室內面積、陽台面積、當層樓地板面積 三列（config 帶 `factory_mode:true`）。
此為專案層級設定，全案各層一體適用；可與下面的陽台過濾疊加。

**A 段陽台過濾**：該層「面積：陽台(原始)」為 0（catalog 無此 display 時用「面積：陽台(最終)」，
`|value|<0.005` 視為 0）→ A 段移除 陽台面積、陽台>2M、室內1/8或8m²、陽台1/8檢討、陽台最終面積
五列（config 帶 `omit_balcony:true`）。一般多棟以「各棟總計該層」判斷；連棟透天對各棟該層都評估，
任一棟>0 就保留全部陽台列。室內面積、當層樓地板面積 兩列一律保留。

標記：(a)僅共用梯廳、(b)僅停車空間面積>0、(c)僅該項面積>0、(d)僅陽台或梯廳面積>0。

**免計容積(B)**（依序）：梯廳(a,c)、安全梯和管委會空間(c)、機電設備空間和管道間(c)、停車空間(c)、騎樓(c)、車道(c)、防空避難室(c)。
col1 標籤：梯廳：／安全梯和管委會空間：／機電設備空間和管道間：／停車空間／騎樓／車道／防空避難室。
（外掛 v0.0.21 前這兩項叫「機電設備」「管道間」；build 腳本的 `section_b` 仍接受舊名。）

**回計容積(C)**（依序）：當層樓地板面積10%(a,d)、當層樓地板面積15%(a,d)、梯廳10%檢討(a,d)、
陽台10%檢討(a,d)、陽台+梯廳15%檢討(a,d)、停車空間回計(b)、裝飾柱回計(c)。
**工廠類建築（factory_mode）時「陽台10%檢討」一律不放**（即使共用且陽台>0——陽台已全額
計入容積、無 10% 回計檢討），其餘 (a)(d) 項不受影響。
col1 標籤：當層樓地板面積10%：／…15%：／梯廳10%檢討：／陽台10%檢討：／陽台+梯廳15%檢討：／停車檢討：／裝飾柱回計：。

判斷用 `evaluate_story_autotext_values` 取各「面積：」值（見 tokens.md），`|value|<0.005` 視為 0。
(a)＝共用梯廳才放；(d)＝面積：梯廳 或 面積：陽台(最終) >0 才放。
連棟透天多欄表：對各棟該層都評估，**任一棟該項>0 就放該列**。
（本 skill 依使用者確認採「非共用移除該列、0 值移除」。）

## 四、儲存格格式（逐欄）

全表 alignment=1（靠左）、textbold=false。textsize：標題 1、其餘 2。newline：值格 3、其餘 0。
charwidth：段標籤 col0＝1、棟別列 col0＝1、其餘 0。

- 標題 col0：segments（樓層名＋容積檢討）。
- 棟別列（columns）：col0 text「棟別」；各棟欄 segments（autotext 棟別，綁該棟 story）。
- 段標籤 col0：text（當層樓地板面積(A)／免計容積(B)／回計容積(C)／(A)-(B)+(C)）。
- 項目名：single/columns 放 col1；blockrows 展開項放 col1（垂直合併）、非展開項 col1 colspan 2。
- 棟別欄（blockrows col2）：展開項逐列 A棟/B棟/小計；非展開項此格被 col1 colspan 蓋住（仍送空格）。
- 值格：single/blockrows 在最後一欄；columns 每棟一欄。segments（算式 autotext，綁該樓層/該棟 story）。
- 空格（被合併蓋住者）：text「」，不帶 story/room。
- 每個有內容的格帶 `storyGuid` 與 `roomGuid`；`roomGuid` 一律 `4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3`（常數照抄）。
- charwidth:1 與 newline 互斥。table_type=normal、不設樣板層級 story_guid/room_guid。框線全 1。
- 欄寬：single [100,183,653]；columns [100,183,各棟≈300]；blockrows [100,150,70,480]（可用 config 覆寫）。

## 四點五、夾層版面（mezz，一般多棟＋夾層）

當某地上層有配對的「…夾層」樓層時，改用夾層版面（欄數＝3＋棟數）：
**col0 項目｜col1 當層/夾層/小計｜各棟欄(A棟/B棟…)｜最後一欄 各棟總計小計**。
**棟別放在上方欄頭列**（col2..＝A棟/B棟…，最後一欄＝小計）；**當層/夾層/小計改放左側 col1**（逐列）。項目分兩類：

- **分棟＋分當層/夾層**（室內面積、陽台(原始)、陽台>2m、**所有 B 段免計項**）：
  項目名（col0）垂直合併跨 3 列（當層/夾層/小計）；col1 逐列放「當層」「夾層」「小計」；
  各棟欄：當層列綁「該棟當層」、夾層列綁「該棟夾層」(無則空)、小計列該棟**留空**（BIMTeki 無每棟小計屬性）；
  最後「各棟總計小計」欄：當層列綁 subtotal_main、夾層列綁 subtotal_mezz。
  **小計列水平合併**：各棟總計小計值(subtotal_story)放 col2、colspan 跨 A棟…小計 各欄（各棟欄不另填）。
- **用小計面積算**（室內1/8或8m²、陽台1/8檢討、陽台最終面積、當層樓地板面積、**所有 C 段回計項**、容積樓地板面積）：
  項目名（col0），值以 colspan 4（col1~col4）合併顯示、綁「各棟總計…小計」樓層。

順序：A 段 split(室內/陽台/陽台>2m) → A 段 merged(室內1/8/陽台1/8/陽台最終/當層樓地板) →
B 段(全 split) → C 段(全 merged) → 容積樓地板面積(merged)。
`omit_balcony:true`／`factory_mode:true` 同樣適用本版面（factory：split 剩 室內面積、陽台(原始)，
merged 剩 當層樓地板面積；omit_balcony：split 只剩室內面積、merged 只剩當層樓地板面積）。此版面不放 A/B/C 段標籤欄。
樓層挑選：只做「各棟總計…小計」存在的地上層；當層綁各棟該層、夾層綁各棟該層夾層(無則空)、小計綁各棟總計小計。
連棟透天＋夾層(mezzcolumns) 為更寬版面，因 per-block 小計/各棟總計常不存在，目前未測。

## 四點六、夾層版面（mezz_single，單棟＋夾層）

單棟案的地上層若有配對「…夾層」樓層與「…小計」樓層（例如「地上四層」＋「地上四層夾層」＋
「地上四層小計」），**合併成一張表，不要拆成三張**。版面為 4 欄：
**col0 項目｜col1 當層｜col2 夾層｜col3 小計**（無棟別維度，不像 mezz 需要各棟欄）。

- **標題**：樓層名稱 autotext 綁「當層」story（回傳如「全一棟地上四層」）＋文字「容積檢討」，
  colspan 4。
- **表頭列**（1 列）：col0「項目」、col1「當層」、col2「夾層」、col3「小計」，皆置中、charwidth 1。
- **split 項目**（室內面積、陽台(原始)、陽台>2m、**所有 B 段免計項**）：每項 1 列——
  col0 項目名，col1 綁「當層」story 的值、col2 綁「夾層」story 的值（該層無夾層對應項目則留空）、
  col3 綁「小計」story 的值。三欄各自是不同的實際數字，不合併。
- **merged 項目**（室內1/8或8m²、陽台1/8檢討、陽台最終面積、當層樓地板面積、**所有 C 段回計項**、
  容積樓地板面積）：每項 1 列——col0 項目名，col1 值格 colspan 3（跨 col1~col3）綁「小計」story，
  因為這些數值本來就是以合併後樓層算的，當層/夾層分開沒有意義；col2、col3 送空白佔位格。
- `omit_balcony:true`／`factory_mode:true` 同樣適用（factory：split 剩 室內面積、陽台(原始)，
  merged 剩 當層樓地板面積；omit_balcony：split 剩室內面積、merged 剩當層樓地板面積）。
- 此版面同樣不放 A/B/C 段標籤欄。
- 樓層挑選：只在單棟樓層清單中存在「…小計」樓層時才用本版面；當層綁該層本身 story、夾層綁配對的
  「…夾層」story、小計綁「…小計」story。

## 五、樓層清單怎麼挑

從 `get_project_autotext_catalog` 的 `storyGuidList`：
- 排除名稱含「屋突」「地下」的樓層，以及名為「總計：」「A棟」「B棟」等虛擬/棟別彙總項。
- 單棟：取各「地上X層」；**若某層存在配對的「…夾層」與「…小計」，三者合併成一張 mezz_single 表，
  不要各自當獨立樓層建三張表**（此為本 skill 曾經犯過的錯誤）。
- 一般多棟：取各「各棟總計地上X層」當該張表主 story；另取各棟同層「X棟地上Y層」供展開列（A棟/B棟…）；
  若該層存在配對的「各棟總計…夾層」與「各棟總計…小計」，同樣合併成一張 mezz 表。
- 連棟透天：取各棟「地上X層」，以**去掉棟別前綴後的樓層名**分組（A棟地上二層＋B棟地上二層＝同一層一張表）；
  每棟一個值欄。棟順序依 get_bimteki_block_unit_settings。

## 六、build_volume_table.py 的 config

```json
{
  "mode": "single | multiblock",
  "title_story": "標題『樓層名』要綁的樓層 guid（多棟給各棟總計該層或任一棟皆可，樓層名不含棟別）",
  "block_prefix": false,
  "story_guid": "single 模式且無 block_rows：所有值格綁的樓層 guid",
  "block_rows": {
    "blocks": [ {"name": "A棟", "story_guid": "A棟該層 guid"}, {"name": "B棟", "story_guid": "B棟該層 guid"} ],
    "subtotal_story": "各棟總計該層 guid"
  },
  "blocks": [ {"story_guid": "A棟該層 guid"}, {"story_guid": "B棟該層 guid"} ],
  "mezzanine_single": { "main": "該層 story guid", "mezz": "該層夾層 story guid", "subtotal": "該層小計 story guid" },
  "factory_mode": false,
  "omit_balcony": false,
  "section_b": ["安全梯和管委會空間", "..."],
  "section_c": ["當層樓地板面積10%", "..."],
  "tokens": { "算式：室內樓地板面積": "${TJL$...}" },
  "value_col_width": 653,
  "item_col_width": 150,
  "block_col_width": 70
}
```
- **單棟（無夾層）**：`mode:"single"`＋`story_guid`（該層），不給 block_rows/blocks/mezzanine* → 3 欄 single 版面。
- **單棟＋夾層**：`mode:"single"`＋`mezzanine_single:{main=該層 guid, mezz=該層夾層 guid, subtotal=該層小計 guid}`
  ＋`title_story`（給 main）→ 4 欄 mezz_single 版面（項目/當層/夾層/小計）。**只要樓層清單裡這層有配對
  的「…夾層」與「…小計」，就一定要用這個 config 分支，不能因為 block_mode=false 就退回普通 single。**
- **一般多棟（無夾層）**：`mode:"single"`＋`block_rows` → 4 欄 blockrows 版面（室內/陽台/陽台>2m 展開＋棟別欄）。
- **一般多棟＋夾層**：`mode:"single"`＋`mezzanine:{blocks:[{name,main=該棟當層,mezz=該棟夾層(選填)}...], subtotal_main=各棟總計當層, subtotal_mezz=各棟總計夾層, subtotal_story=各棟總計小計}`＋`title_story` → 5 欄 mezz 版面（各棟＋小計列）。
- **連棟透天**：`mode:"multiblock"`＋`blocks` → 3＋棟數 欄 columns 版面（含棟別列）。
- `factory_mode`：工廠類建築（`review_settings.balcony_in_floor_area.value` 為 true，見第三節）時設 true，
  A 段只保留 室內面積、陽台面積、當層樓地板面積（各版面皆適用，可與 omit_balcony 疊加）。
- `omit_balcony`：該層陽台面積為 0（判斷見第三節）時設 true，A 段移除陽台相關五列（各版面皆適用）。
- `section_b`/`section_c`：依第三節判斷後、**依表列順序**放入的 key 陣列（可空）。
- `tokens`：選填覆寫預設；`*_col_width`：選填覆寫欄寬。
- 輸出 `cells` 直接餵 `create_project_table_template`；`merges`/`column_widths` 於 `modify` 帶入。
