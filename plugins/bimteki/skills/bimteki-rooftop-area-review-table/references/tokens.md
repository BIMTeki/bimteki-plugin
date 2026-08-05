# 屋突面積檢討表 — display → token 對照

三個值欄全部是**樓層屬性（story 相依，targetType=story、needGUID=true）**，依放置樓層與其棟別解析。
**務必以 `get_project_autotext_catalog` 依 display 比對重取 token**；以下為西區後壠子段實測、屬各案專屬，勿硬編跨案。

## 標題與屋突面積（storyArea）
| display | token（該案） |
|----|----|
| 樓層名稱 | ${TJL$F25387D152474} |
| 棟別 | ${TJL$F5076BDCC0064} |
| 算式：室內樓地板面積（屋突面積預設） | ${TJL$F8FC213D2D115} |
| 算式：屋突（story-relative 屋突面積替代） | 依 catalog 取得 |

## 允建屋突面積、檢討（roofArea，story 相依、通用名稱不分棟）
| 表列 | display | token（該案） |
|----|----|----|
| 允建屋突面積 | 算式：屋突允建面積 | ${TJL$F622E2DB87002} |
| 允建屋突面積（純值） | 面積：屋突允建面積 | ${TJL$F9B73CEA04F88} |
| 檢討 | 算式：屋突檢討式 | ${TJL$FCE11626AE7D2} |
| 屋突建築面積來源（進階） | 算式：屋突建築面積來源 | ${TJL$F193BE9E45C39} |
| 屋突建築面積來源（純值） | 面積：屋突建築面積來源 | ${TJL$FC9AE408D3781} |

註：這些 roofArea token 過去為「逐棟固定欄位型」；現已改為 story 相依通用 token，
單一 story-open 樣板即可依放置樓層自動解析各棟各屋突層的值。
