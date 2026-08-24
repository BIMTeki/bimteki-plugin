#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建 XX層容積檢討表 的儲存格 payload 產生器。

版面（由 config 決定）：
  single      單棟：3 欄（段標籤／項目／值）。
  columns     連棟透天：3＋棟數 欄（段標籤／項目／各棟值），標題後有棟別列。
  blockrows   一般多棟(無夾層)：4 欄（段標籤／項目／棟別／值）。室內/陽台/陽台>2m 分棟＋小計。
  mezz_single 單棟(有夾層)：4 欄＝項目/當層/夾層/小計。split 項目(室內/陽台/陽台>2m/所有B項)三欄各自
              綁該層/夾層/小計 story 的實際值；merged 項目(其餘 A 項/所有C項/容積樓地板面積)以
              colspan 3 顯示單一小計值。判斷與棟數無關：只要該層有配對「…夾層」樓層就必須走這裡，
              不能因為 block_mode=false 就退回 single 版面把三個 story 拆成三張表。
  mezz        一般多棟(有夾層)：欄=項目/當層夾層小計/各棟.../各棟總計小計；棟別(A棟/B棟/小計)在上方欄頭。
              分棟＋分當層/夾層（室內、陽台、陽台>2m、所有 B 項）：項目名垂直合併跨各棟列，
              各棟列(A棟/B棟)當層綁該棟當層、夾層綁該棟夾層(無則空)、小計欄空；末尾再加一列「小計」＝各棟總計當層/夾層/小計。
              用小計面積算（室內1/8、陽台1/8、陽台最終、當層樓地板、所有 C 項、容積樓地板）：
              項目名一欄，值以 colspan 合併顯示、綁各棟總計小計屬性。
  mezzcolumns 連棟透天(有夾層)：項目 ＋ 各棟(當層/夾層/小計) 欄群（未測；per-block 小計/各棟總計常不存在，留空）。

用法：python build_volume_table.py config.json   （或 < config.json）
輸出（stdout, JSON）：{ cols, rows, room_guid, cells, merges, column_widths }
config 欄位見 references/table-structure.md 第六節。
"""
import json, sys

DEFAULT_TOKENS = {
    "樓層名稱": "${TJL$F25387D152474}",
    "棟別": "${TJL$F5076BDCC0064}",
    "算式：室內樓地板面積": "${TJL$F8FC213D2D115}",
    "算式：陽台(原始)": "${TJL$F44FE114E765F}",
    "算式：陽台>2m": "${TJL$F2B860D23D446}",
    "算式：室內樓地板面積1/8或8m²": "${TJL$F9A36B859CBC7}",
    "算式：陽台超過1/8回計": "${TJL$FF360751F1291}",
    "算式：陽台(最終)": "${TJL$FC62A32757EC0}",
    "算式：當層樓地板面積": "${TJL$FABF14ACF645B}",
    "算式：梯廳": "${TJL$F32E78E8DB7E2}",
    "算式：機電設備": "${TJL$F09DF9BDF9548}",
    "算式：管道間": "${TJL$F29265BDA5983}",
    "算式：停車空間": "${TJL$FA930DA8E8F5D}",
    "算式：騎樓": "${TJL$FC9442BCF7BA2}",
    "算式：車道": "${TJL$F57C2F2547AA7}",
    "算式：防空避難室": "${TJL$FEFF3EBF2229C}",
    "算式：當層樓地板面積10%": "${TJL$FA75840A684A6}",
    "算式：當層樓地板面積15%": "${TJL$F5ED8E1F59371}",
    "算式：梯廳超過10%回計": "${TJL$F7C6AEFC6E58E}",
    "算式：陽台超過10%回計": "${TJL$F5D88CB0B7139}",
    "算式：陽台+梯廳": "${TJL$F4FB6F42DB13B}",
    "算式：陽台+梯廳超過15%回計": "${TJL$F083C5933CE1F}",
    "算式：停車空間回計": "${TJL$F548C26194934}",
    "算式：裝飾柱回計": "${TJL$F127A747989D4}",
    "算式：容積樓地板面積": "${TJL$F42CBE2E770BF}",
}
ROOM_GUID_DEFAULT = "4f8303bf-26fd-4a53-9fe7-2a7c13fdf3d3"

# (col1 標籤, [算式 display], expandable/split)
SECTION_A = [
    ("室內面積：",     ["算式：室內樓地板面積"],       True),
    ("陽台面積：",     ["算式：陽台(原始)"],           True),
    ("陽台>2M：",      ["算式：陽台>2m"],              True),
    ("室內1/8或8m²：", ["算式：室內樓地板面積1/8或8m²"], False),
    ("陽台1/8檢討：",  ["算式：陽台超過1/8回計"],       False),
    ("陽台最終面積：", ["算式：陽台(最終)"],           False),
    ("當層樓地板面積：", ["算式：當層樓地板面積"],       False),
]
ITEM_B = {
    "梯廳":      ("梯廳：",   ["算式：梯廳"]),
    "機電設備":  ("機電設備：", ["算式：機電設備"]),
    "管道間":    ("管道間：", ["算式：管道間"]),
    "停車空間":  ("停車空間", ["算式：停車空間"]),
    "騎樓":      ("騎樓",    ["算式：騎樓"]),
    "車道":      ("車道",    ["算式：車道"]),
    "防空避難室": ("防空避難室", ["算式：防空避難室"]),
}
ITEM_C = {
    "當層樓地板面積10%": ("當層樓地板面積10%：", ["算式：當層樓地板面積10%"]),
    "當層樓地板面積15%": ("當層樓地板面積15%：", ["算式：當層樓地板面積15%"]),
    "梯廳10%檢討":       ("梯廳10%檢討：",       ["算式：梯廳超過10%回計"]),
    "陽台10%檢討":       ("陽台10%檢討：",       ["算式：陽台超過10%回計"]),
    "陽台+梯廳15%檢討":  ("陽台+梯廳15%檢討：",  ["算式：陽台+梯廳", "算式：陽台+梯廳超過15%回計"]),
    "停車空間回計":      ("停車檢討：",          ["算式：停車空間回計"]),
    "裝飾柱回計":        ("裝飾柱回計：",        ["算式：裝飾柱回計"]),
}
FINAL_ITEM = ("容積樓地板面積：", ["算式：容積樓地板面積"])

# 陽台面積為 0 時（config omit_balcony=true）A 段要移除的列
BALCONY_A_LABELS = {"陽台面積：", "陽台>2M：", "室內1/8或8m²：", "陽台1/8檢討：", "陽台最終面積："}
# 工廠類建築（陽台全額計入容積，config factory_mode=true）時 A 段只保留的列
FACTORY_A_LABELS = {"室內面積：", "陽台面積：", "當層樓地板面積："}


def tok(tokens, display):
    if display not in tokens:
        raise SystemExit("缺 token：%s（請由 catalog 取得並放進 config.tokens）" % display)
    return tokens[display]


def value_segments(tokens, displays):
    segs = []
    for i, d in enumerate(displays):
        if i:
            segs.append({"type": "text", "value": "，"})
        segs.append({"type": "autotext", "token": tok(tokens, d)})
    return segs


def build(cfg):
    tokens = dict(DEFAULT_TOKENS)
    tokens.update(cfg.get("tokens") or {})
    room = cfg.get("room_guid", ROOM_GUID_DEFAULT)
    mode = cfg["mode"]
    sec_b = cfg.get("section_b", [])
    sec_c = cfg.get("section_c", [])
    section_a = SECTION_A
    if cfg.get("factory_mode"):
        section_a = [it for it in section_a if it[0] in FACTORY_A_LABELS]
        sec_c = [k for k in sec_c if k != "陽台10%檢討"]  # 陽台全額計入，無 10% 回計檢討
    if cfg.get("omit_balcony"):
        section_a = [it for it in section_a if it[0] not in BALCONY_A_LABELS]
    block_rows = cfg.get("block_rows")
    mezz = cfg.get("mezzanine")           # 一般多棟＋夾層
    mezz_single = cfg.get("mezzanine_single")  # 單棟＋夾層
    mezzcols = cfg.get("mezzanine_columns")  # 連棟透天＋夾層（未測）

    cells = []
    merges = []

    def put(row, col, **kw):
        c = {"row": row, "col": col}
        c.update(kw)
        cells.append(c)

    # ---- mezz_single 版面（單棟＋夾層）：獨立處理 ----
    if mezz_single:
        main_story = mezz_single["main"]
        mezz_story = mezz_single.get("mezz")
        subtotal = mezz_single["subtotal"]
        title_story = cfg.get("title_story") or main_story
        ncols = 4  # 項目|當層|夾層|小計

        def slab(row, col, text, cw=0, al=1, story=None):
            put(row, col, text=text, storyGuid=story or subtotal, roomGuid=room,
                alignment=al, charwidth=cw, newline=0, textsize=2, textbold=False)

        def sempty(row, col):
            put(row, col, text="", alignment=1, charwidth=0, newline=0, textsize=2, textbold=False)

        def sval(row, col, disp, story):
            put(row, col, segments=value_segments(tokens, disp), storyGuid=story, roomGuid=room,
                alignment=1, charwidth=0, newline=3, textsize=2, textbold=False)

        put(0, 0, segments=[{"type": "autotext", "token": tok(tokens, "樓層名稱")},
                            {"type": "text", "value": "容積檢討"}],
            storyGuid=title_story, roomGuid=room,
            alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
        for col in range(1, ncols):
            put(0, col, text="", alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
        merges.append({"row": 0, "col": 0, "colspan": ncols, "rowspan": 1})

        slab(1, 0, "項目", cw=1, al=2)
        slab(1, 1, "當層", cw=1, al=2)
        slab(1, 2, "夾層", cw=1, al=2)
        slab(1, 3, "小計", cw=1, al=2)

        split_items, merged_items = [], []
        for lbl, disp, is_split in section_a:
            (split_items if is_split else merged_items).append((lbl, disp))
        b_items = [(ITEM_B[k][0], ITEM_B[k][1]) for k in sec_b]      # split
        c_items = [(ITEM_C[k][0], ITEM_C[k][1]) for k in sec_c]      # merged

        r = 2
        seq = ([("split", it) for it in split_items] +
               [("merged", it) for it in merged_items] +
               [("split", it) for it in b_items] +
               [("merged", it) for it in c_items] +
               [("merged", FINAL_ITEM)])
        for kind, (lbl, disp) in seq:
            if kind == "split":
                slab(r, 0, lbl)
                sval(r, 1, disp, main_story)
                sval(r, 2, disp, mezz_story) if mezz_story else sempty(r, 2)
                sval(r, 3, disp, subtotal)
            else:  # merged：項目名＋合併小計值（跨 col1~col3）
                slab(r, 0, lbl)
                sval(r, 1, disp, subtotal)
                merges.append({"row": r, "col": 1, "colspan": ncols - 1, "rowspan": 1})
                sempty(r, 2)
                sempty(r, 3)
            r += 1

        cw = cfg.get("column_widths") or [180, 220, 220, 220]
        return {"cols": ncols, "rows": r, "room_guid": room,
                "cells": cells, "merges": merges, "column_widths": cw}

    # ---- mezz 版面（一般多棟＋夾層）：獨立處理 ----
    if mezz:
        mblocks = mezz["blocks"]           # [{name, main, mezz(optional)}]
        subtotal = mezz["subtotal_story"]  # 各棟總計小計 story
        title_story = cfg.get("title_story") or mblocks[0]["main"]
        ncols = 3 + len(mblocks)  # 項目|當層夾層小計|各棟...|各棟總計小計

        def mlab(row, col, text, cw=0, al=1, story=None):
            put(row, col, text=text, storyGuid=story or subtotal, roomGuid=room,
                alignment=al, charwidth=cw, newline=0, textsize=2, textbold=False)

        def mempty(row, col):
            put(row, col, text="", alignment=1, charwidth=0, newline=0, textsize=2, textbold=False)

        def mval(row, col, disp, story):
            put(row, col, segments=value_segments(tokens, disp), storyGuid=story, roomGuid=room,
                alignment=1, charwidth=0, newline=3, textsize=2, textbold=False)

        # row0 標題
        put(0, 0, segments=[{"type": "autotext", "token": tok(tokens, "樓層名稱")},
                            {"type": "text", "value": "容積檢討"}],
            storyGuid=title_story, roomGuid=room,
            alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
        for col in range(1, ncols):
            put(0, col, text="", alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
        merges.append({"row": 0, "col": 0, "colspan": ncols, "rowspan": 1})

        nb = len(mblocks)
        sub_col = 2 + nb  # 各棟總計小計欄

        # row1 欄頭：棟別放上方（A棟/B棟…/小計）；左側 col1 放當層/夾層/小計
        mlab(1, 0, "項目", cw=1, al=2)
        mempty(1, 1)
        for i, b in enumerate(mblocks):
            mlab(1, 2 + i, b["name"], cw=1, al=2)
        mlab(1, sub_col, "小計", cw=1, al=2)

        split_items, merged_items = [], []
        for lbl, disp, is_split in section_a:
            (split_items if is_split else merged_items).append((lbl, disp))
        b_items = [(ITEM_B[k][0], ITEM_B[k][1]) for k in sec_b]      # split
        c_items = [(ITEM_C[k][0], ITEM_C[k][1]) for k in sec_c]      # merged

        sub_main = mezz.get("subtotal_main")  # 各棟總計當層
        sub_mezz = mezz.get("subtotal_mezz")  # 各棟總計夾層

        r = 2
        seq = ([("split", it) for it in split_items] +
               [("merged", it) for it in merged_items] +
               [("split", it) for it in b_items] +
               [("merged", it) for it in c_items] +
               [("merged", FINAL_ITEM)])
        for kind, (lbl, disp) in seq:
            if kind == "split":
                stem = lbl[:-1] if lbl.endswith("：") else lbl
                start = r
                # 左側三列：當層／夾層／小計
                for j, axname in enumerate(["當層", "夾層", "小計"]):
                    if j == 0:
                        mlab(r, 0, stem)          # 項目名（rowspan 3）
                    else:
                        mempty(r, 0)
                    mlab(r, 1, axname)            # 當層/夾層/小計（左側）
                    if axname == "小計":
                        # 小計列水平合併：各棟總計小計值放 col2、跨 A棟…小計 各欄
                        mval(r, 2, disp, subtotal)
                        merges.append({"row": r, "col": 2, "colspan": nb + 1, "rowspan": 1})
                        for c in range(3, sub_col + 1):
                            mempty(r, c)
                    else:
                        for i, b in enumerate(mblocks):
                            if axname == "當層":
                                mval(r, 2 + i, disp, b["main"])
                            else:  # 夾層
                                mval(r, 2 + i, disp, b["mezz"]) if b.get("mezz") else mempty(r, 2 + i)
                        if axname == "當層":
                            mval(r, sub_col, disp, sub_main) if sub_main else mempty(r, sub_col)
                        else:
                            mval(r, sub_col, disp, sub_mezz) if sub_mezz else mempty(r, sub_col)
                    r += 1
                merges.append({"row": start, "col": 0, "colspan": 1, "rowspan": 3})
            else:  # merged：項目名＋合併小計值
                mlab(r, 0, lbl)
                mval(r, 1, disp, subtotal)
                merges.append({"row": r, "col": 1, "colspan": ncols - 1, "rowspan": 1})
                for c in range(2, ncols):
                    mempty(r, c)
                r += 1

        cw = cfg.get("column_widths") or ([150, 70] + [140] * (nb + 1))
        return {"cols": ncols, "rows": r, "room_guid": room,
                "cells": cells, "merges": merges, "column_widths": cw}

    # ---- 其餘版面（single / columns / blockrows）----
    if mode == "multiblock":
        blocks = cfg["blocks"]
        value_stories = [b["story_guid"] for b in blocks]
        base_story = value_stories[0]
        ncols = 2 + len(blocks)
        layout = "columns"
    elif block_rows:
        base_story = block_rows["subtotal_story"]
        ncols = 4
        layout = "blockrows"
    else:
        base_story = cfg["story_guid"]
        value_stories = [base_story]
        ncols = 3
        layout = "single"

    def empty(row, col):
        put(row, col, text="", alignment=1, charwidth=0, newline=0, textsize=2, textbold=False)

    def lab(row, col, text, cw=0, story=None):
        put(row, col, text=text, storyGuid=story or base_story, roomGuid=room,
            alignment=1, charwidth=cw, newline=0, textsize=2, textbold=False)

    def val(row, col, disp, story):
        put(row, col, segments=value_segments(tokens, disp), storyGuid=story, roomGuid=room,
            alignment=1, charwidth=0, newline=3, textsize=2, textbold=False)

    if cfg.get("block_prefix"):
        title_segs = [{"type": "autotext", "token": tok(tokens, "棟別")}, {"type": "text", "value": "："},
                      {"type": "autotext", "token": tok(tokens, "樓層名稱")}, {"type": "text", "value": "容積檢討"}]
    else:
        title_segs = [{"type": "autotext", "token": tok(tokens, "樓層名稱")}, {"type": "text", "value": "容積檢討"}]
    put(0, 0, segments=title_segs, storyGuid=cfg["title_story"], roomGuid=room,
        alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
    for col in range(1, ncols):
        put(0, col, text="", alignment=1, charwidth=0, newline=0, textsize=1, textbold=False)
    merges.append({"row": 0, "col": 0, "colspan": ncols, "rowspan": 1})

    r = 1
    if layout == "columns":
        lab(r, 0, "棟別", cw=1)
        empty(r, 1)
        for i, b in enumerate(blocks):
            put(r, 2 + i, segments=[{"type": "autotext", "token": tok(tokens, "棟別")}],
                storyGuid=b["story_guid"], roomGuid=room,
                alignment=1, charwidth=0, newline=0, textsize=2, textbold=False)
        r += 1

    def emit_simple(section_label, rows):
        nonlocal r
        start = r
        n = len(rows)
        for j, row in enumerate(rows):
            lab(r, 0, section_label, cw=1) if j == 0 else empty(r, 0)
            lab(r, 1, row["label"])
            if layout == "columns":
                for i, st in enumerate(value_stories):
                    val(r, 2 + i, row["disp"], st)
            else:
                val(r, 2, row["disp"], row.get("story", base_story))
            r += 1
        if n > 1:
            merges.append({"row": start, "col": 0, "colspan": 1, "rowspan": n})

    def emit_blockrows(section_label, items):
        nonlocal r
        start = r
        phys = []
        for it in items:
            if it["expandable"]:
                bs = block_rows["blocks"]
                stem = it["label"][:-1] if it["label"].endswith("：") else it["label"]
                for k, b in enumerate(bs):
                    phys.append({"col1": stem if k == 0 else None,
                                 "col1_rowspan": len(bs) + 1 if k == 0 else None,
                                 "col2": b["name"], "disp": it["disp"], "story": b["story_guid"]})
                phys.append({"col1": None, "col2": "小計", "disp": it["disp"],
                             "story": block_rows["subtotal_story"]})
            else:
                phys.append({"col1": it["label"], "col1_colspan": 2, "col2": None,
                             "disp": it["disp"], "story": base_story})
        n = len(phys)
        for j, p in enumerate(phys):
            lab(r, 0, section_label, cw=1) if j == 0 else empty(r, 0)
            if p.get("col1") is not None:
                lab(r, 1, p["col1"])
            else:
                empty(r, 1)
            if p.get("col1_rowspan"):
                merges.append({"row": r, "col": 1, "colspan": 1, "rowspan": p["col1_rowspan"]})
            if p.get("col1_colspan"):
                merges.append({"row": r, "col": 1, "colspan": p["col1_colspan"], "rowspan": 1})
            if p.get("col2") is not None:
                lab(r, 2, p["col2"])
            else:
                empty(r, 2)
            val(r, 3, p["disp"], p["story"])
            r += 1
        if n > 1:
            merges.append({"row": start, "col": 0, "colspan": 1, "rowspan": n})

    final_label = "(A)" + ("-(B)" if sec_b else "") + ("+(C)" if sec_c else "")

    if layout == "blockrows":
        emit_blockrows("當層樓地板面積(A)",
                       [{"label": l, "disp": d, "expandable": e} for (l, d, e) in section_a])
        if sec_b:
            emit_blockrows("免計容積(B)",
                           [{"label": ITEM_B[k][0], "disp": ITEM_B[k][1], "expandable": False} for k in sec_b])
        if sec_c:
            emit_blockrows("回計容積(C)",
                           [{"label": ITEM_C[k][0], "disp": ITEM_C[k][1], "expandable": False} for k in sec_c])
        emit_blockrows(final_label, [{"label": FINAL_ITEM[0], "disp": FINAL_ITEM[1], "expandable": False}])
        column_widths = [100, cfg.get("item_col_width", 150), cfg.get("block_col_width", 70),
                         cfg.get("value_col_width", 480)]
    else:
        emit_simple("當層樓地板面積(A)", [{"label": l, "disp": d} for (l, d, e) in section_a])
        if sec_b:
            emit_simple("免計容積(B)", [{"label": ITEM_B[k][0], "disp": ITEM_B[k][1]} for k in sec_b])
        if sec_c:
            emit_simple("回計容積(C)", [{"label": ITEM_C[k][0], "disp": ITEM_C[k][1]} for k in sec_c])
        emit_simple(final_label, [{"label": FINAL_ITEM[0], "disp": FINAL_ITEM[1]}])
        vw = cfg.get("value_col_width", 653 if layout == "single" else 300)
        column_widths = [100, 183] + [vw] * (ncols - 2)

    return {"cols": ncols, "rows": r, "room_guid": room,
            "cells": cells, "merges": merges, "column_widths": column_widths}


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else json.load(sys.stdin)
    sys.stdout.write(json.dumps(build(cfg), ensure_ascii=False))


if __name__ == "__main__":
    main()
