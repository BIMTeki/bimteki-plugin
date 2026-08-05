#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建「地下層容積檢討」表（地下層總計容積檢討表）的儲存格 payload 產生器。

這張表全案只有一張（不分棟）：上半用**一個陣列自動文字**「地下層停車清單」
(ParkingInfoStoryManager.ParkingInfoStories) 放置時自動逐樓層展開，
下半是小計列與檢討區塊（防空避難設備面積、可扣容積總計、檢討式）。

版面（欄數 = 可見陣列欄位數，預設 4）：
  row0  標題「地下層容積檢討」            （col0，colspan=ncols）
  row1  欄頭（手打文字，順序需與 columns 一致）
  row2  陣列根 ARRAY_AUTOTEXT_V1（col0，其餘欄留空佔位）——放置時往下展開多列
  row3  小計                             （各欄綁「數量/面積：地下層總計…」token）
  row4  檢討：                            （divider，col0 colspan=ncols，空值）
  row5  防空避難設備面積：               （col1 綁「面積：法定防空避難室面積」＋文字，colspan=ncols-1）
  row6  可扣容積總計：                   （col1 綁「算式：地下層可扣容積」，colspan=ncols-1）
  row7  檢討：                            （col1 綁「算式：地下室容積檢討式」，colspan=ncols-1）

用法：python build_basement_table.py config.json   （或 < config.json）
輸出（stdout, JSON）：{ cols, rows, room_guid, cells, merges, column_widths }
config 欄位見 references/table-structure.md。
"""
import json, sys

ROOM_GUID_DEFAULT = "4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3"

# 陣列「地下層停車清單」可用欄位（fieldName 需逐字對；由 get_project_table_templates 讀 sample 或
# get_project_autotext_catalog(category="arrayField") 佐證）。
ARRAY_SOURCE_TOKEN = "ParkingInfoStoryManager.ParkingInfoStories"
ARRAY_FIELDS_AVAILABLE = ["樓層", "樓地板面積", "汽車位數", "機車位數", "自行車位數", "可扣容積計算式"]

# 各陣列欄位 → 小計列該欄要綁的「總計」token（volumeCheck，路徑 容積檢討/地下層免計容積檢討/總計）。
# 樓層欄的小計格放文字「小計」；沒有對應總計 token 的欄位（如可扣容積計算式）小計格留空。
SUBTOTAL_TOKENS = {
    "汽車位數":   "數量：地下層總計汽車停車位數",   # ${TJL$FB92F011BC7FF}
    "機車位數":   "數量：地下層總計機車停車位數",   # ${TJL$F32C0743E2966}
    "自行車位數": "數量：地下層總計自行車停車位數", # ${TJL$F1ABD882E5DE2}
    "樓地板面積": "面積：地下層總計樓地板面積",     # ${TJL$FD90579BEFCB9}
}

# 檢討區塊各值格要綁的 token（display）。
CHECK_TOKENS = {
    "防空避難室面積":     "面積：法定防空避難室面積",         # ${TJL$FDB4E6D7607F2}（分類 coverage/建蔽率相關）
    "地下層可扣容積算式": "算式：地下層可扣容積",             # ${TJL$F9DDB487BBF2A}
    "地下室容積檢討式":   "算式：地下室容積檢討式",           # ${TJL$FF4CBAA811ADC}
    "地下層樓地板總計":   "算式：地下層樓地板面積總計(含車道)", # ${TJL$FA76D466BC8B6}（選用的地下層樓地板面積列）
}

# 實測穩定的預設 token（同一份 BIMTeki 專案家族）。仍建議以 catalog display 比對確認，
# 有出入時放進 config 的 tokens 覆寫，不要硬編。
DEFAULT_TOKENS = {
    "數量：地下層總計汽車停車位數":   "${TJL$FB92F011BC7FF}",
    "數量：地下層總計機車停車位數":   "${TJL$F32C0743E2966}",
    "數量：地下層總計自行車停車位數": "${TJL$F1ABD882E5DE2}",
    "面積：地下層總計樓地板面積":     "${TJL$FD90579BEFCB9}",
    "面積：法定防空避難室面積":       "${TJL$FDB4E6D7607F2}",
    "算式：地下層可扣容積":           "${TJL$F9DDB487BBF2A}",
    "算式：地下室容積檢討式":         "${TJL$FF4CBAA811ADC}",
    "算式：地下層樓地板面積總計(含車道)": "${TJL$FA76D466BC8B6}",
}

# 欄頭預設顯示名（可用 config.header_labels 覆寫；樓地板面積習慣加單位）。
HEADER_LABELS = {
    "樓層": "樓層", "汽車位數": "汽車位數", "機車位數": "機車位數",
    "自行車位數": "自行車位數", "樓地板面積": "樓地板面積(m²)", "可扣容積計算式": "可扣容積",
}


def tok(tokens, display):
    if display not in tokens:
        raise SystemExit("缺 token：%s（請由 catalog 取得並放進 config.tokens）" % display)
    return tokens[display]


def build(cfg):
    tokens = dict(DEFAULT_TOKENS)
    tokens.update(cfg.get("tokens") or {})
    room = cfg.get("room_guid", ROOM_GUID_DEFAULT)
    story = cfg["story_guid"]                      # 全案總計 story guid（見 SKILL.md）
    columns = cfg.get("columns") or ["樓層", "汽車位數", "機車位數", "樓地板面積"]
    for c in columns:
        if c not in ARRAY_FIELDS_AVAILABLE:
            raise SystemExit("未知陣列欄位：%s（可用：%s）" % (c, "/".join(ARRAY_FIELDS_AVAILABLE)))
    if columns[0] != "樓層":
        raise SystemExit("第一欄需為『樓層』（陣列根固定放 col0）。")
    header_labels = dict(HEADER_LABELS); header_labels.update(cfg.get("header_labels") or {})
    include_floor_area_row = cfg.get("include_floor_area_row", False)  # 是否加「地下層樓地板面積：」列（sample 有、本案圖無）
    ncols = len(columns)

    cells, merges = [], []

    def put(row, col, **kw):
        d = {"row": row, "col": col}; d.update(kw); cells.append(d)

    def txt(row, col, t, size=2, ctx=True):
        d = dict(text=t, alignment=1, charwidth=0, newline=0, textsize=size, textbold=False, roomGuid=room)
        if ctx: d["storyGuid"] = story
        put(row, col, **d)

    def empty(row, col, size=2):
        put(row, col, text="", alignment=1, charwidth=0, newline=0, textsize=size, textbold=False)

    def val(row, col, display, extra_text=None):
        segs = [{"type": "autotext", "token": tok(tokens, display)}]
        if extra_text:
            segs.append({"type": "text", "value": extra_text})
        put(row, col, segments=segs, alignment=1, charwidth=0, newline=0,
            textsize=2, textbold=False, roomGuid=room, storyGuid=story)

    # row0 標題
    txt(0, 0, "地下層容積檢討", size=1)
    for c in range(1, ncols): empty(0, c, size=1)
    merges.append({"row": 0, "col": 0, "colspan": ncols, "rowspan": 1})

    # row1 欄頭（文字，順序＝columns）
    for c, field in enumerate(columns):
        txt(1, c, header_labels.get(field, field))

    # row2 陣列根（col0）＋佔位
    array_meta = {
        "sourceAutoTextToken": ARRAY_SOURCE_TOKEN,
        "columnSettings": [
            {"fieldName": f, "isVisible": True, "displayOrder": i} for i, f in enumerate(columns)
        ],
        "fieldsOrientation": 0, "targetType": -858993460, "needGUID": False,
        "propSettingName": "", "isTemplateGUID": False, "targetGUID": "",
    }
    put(2, 0, is_array_autotext_root=True,
        originaldata="ARRAY_AUTOTEXT_V1:" + json.dumps(array_meta, ensure_ascii=False),
        alignment=1, charwidth=0, newline=0, textsize=2, textbold=False,
        roomGuid=room, storyGuid=story)
    for c in range(1, ncols): empty(2, c)

    # row3 小計
    txt(3, 0, "小計")
    for c, field in enumerate(columns):
        if c == 0:
            continue
        disp = SUBTOTAL_TOKENS.get(field)
        if disp:
            val(3, c, disp)
        else:
            empty(3, c)

    r = 4
    # 檢討：divider
    txt(r, 0, "檢討：")
    for c in range(1, ncols): empty(r, c)
    merges.append({"row": r, "col": 0, "colspan": ncols, "rowspan": 1})
    r += 1

    # 選用：地下層樓地板面積：（sample 有此列；本案圖無，預設關）
    if include_floor_area_row:
        txt(r, 0, "地下層樓地板面積：")
        val(r, 1, CHECK_TOKENS["地下層樓地板總計"])
        for c in range(2, ncols): empty(r, c)
        merges.append({"row": r, "col": 1, "colspan": ncols - 1, "rowspan": 1})
        r += 1

    # 防空避難設備面積：
    txt(r, 0, "防空避難設備面積：")
    val(r, 1, CHECK_TOKENS["防空避難室面積"], extra_text="m² (按建築面積附建)")
    for c in range(2, ncols): empty(r, c)
    merges.append({"row": r, "col": 1, "colspan": ncols - 1, "rowspan": 1})
    r += 1

    # 可扣容積總計：
    txt(r, 0, "可扣容積總計：")
    val(r, 1, CHECK_TOKENS["地下層可扣容積算式"])
    for c in range(2, ncols): empty(r, c)
    merges.append({"row": r, "col": 1, "colspan": ncols - 1, "rowspan": 1})
    r += 1

    # 檢討：（最終結果）
    txt(r, 0, "檢討：")
    val(r, 1, CHECK_TOKENS["地下室容積檢討式"])
    for c in range(2, ncols): empty(r, c)
    merges.append({"row": r, "col": 1, "colspan": ncols - 1, "rowspan": 1})
    r += 1

    # 欄寬：樓層欄較窄、其餘平均分配（可用 config.column_widths 覆寫）
    default_widths = [150] + [max(90, int(520 / max(1, ncols - 1)))] * (ncols - 1)
    column_widths = cfg.get("column_widths") or default_widths

    return {"cols": ncols, "rows": r, "room_guid": room,
            "cells": cells, "merges": merges, "column_widths": column_widths}


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else json.load(sys.stdin)
    sys.stdout.write(json.dumps(build(cfg), ensure_ascii=False))


if __name__ == "__main__":
    main()
